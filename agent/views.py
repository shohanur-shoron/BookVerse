# Add this near the other helper functions in views.py
import google.generativeai as genai
import os
import json
import time
import uuid
import traceback
from datetime import datetime

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse, Http404
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count

from book.models import Book, Favorite, ReadingStatus

try:
    api_key = 'API Key'
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    summary_model = genai.GenerativeModel('gemini-1.5-flash-latest')

except Exception as e:
    print(f"FATAL ERROR: Could not configure Gemini API: {e}")
    model = None
    summary_model = None

def get_full_prompt(user_query):
    system_prompt = """
You are an AI assistant specialized in interpreting user requests related to managing their personal book library, specifically their 'Favorites' list and 'Reading Status'.
Your task is to analyze the user's natural language query and translate it into a precise JSON object (or an array of JSON objects if multiple distinct requests are detected) representing the intended action(s).

Based ONLY on the User Query provided:
1.  Identify if the query contains one or multiple distinct requests.
2.  For each distinct request, identify the primary entity: 'favourite_list' or 'reading_status'.
3.  For each distinct request, determine the specific operation (e.g., view, count, add, remove, update status).
4.  For each distinct request, extract necessary parameters (e.g., 'book_name', 'status').
5.  Construct the appropriate JSON output according to the rules below.

**Output Requirements:**
*   **Single Request:** If the query contains *only one* discernible request matching the definitions below, you MUST respond ONLY with a *single*, valid JSON object following the specified structure.
*   **Multiple Requests:** If the query clearly contains *multiple distinct requests* (e.g., "Show my favorites and count them"), you MUST respond ONLY with a JSON *array*, where each element is a valid JSON object representing one of the distinct requests, following the specified structure.
*   **Strict JSON Only:** Do NOT include any introductory text, explanations, apologies, greetings, or markdown formatting like ```json ... ``` before or after the JSON object or JSON array. Your entire response must be *only* the valid JSON.
*   **Unknown/Ambiguous:** If the user's query (or any part of a multi-request query) is ambiguous, unclear, or does not map to the defined actions/operations below, represent that part with: `{"action": "unknown", "operation": "unknown", "parameters": {}}`. If the *entire* query is unknown, return just that single unknown object. If part of a multi-request is unknown, include the unknown object in the array along with recognized ones.

**Defined Actions, Operations, Parameters, and EXACT JSON Output Templates:**

**1. Action Type: `favourite_list`** (Interacting with the user's list of favorite books)

*   **Operation: `show_all`**
    *   Triggered by: User wants to see their list of favorite books.
    *   Example Queries: "Show my favorite books", "List my favorites"
    *   JSON Output Template:
        ```json
        { "action": "favourite_list", "operation": "show_all", "parameters": {} }
        ```
*   **Operation: `count`**
    *   Triggered by: User wants to know the number of books in their favorites.
    *   Example Queries: "How many favorites do I have?", "Count my favorite books."
    *   JSON Output Template:
        ```json
        { "action": "favourite_list", "operation": "count", "parameters": {} }
        ```
*   **Operation: `add`**
    *   Triggered by: User wants to add a specific book to their favorites.
    *   Requires Parameter: `book_name` (string).
    *   Example Queries: "Add 'The Great Gatsby' to my favorites", "Favorite '1984'".
    *   JSON Output Template (Example):
        ```json
        { "action": "favourite_list", "operation": "add", "parameters": { "book_name": "The Great Gatsby" } }
        ```
*   **Operation: `remove`**
    *   Triggered by: User wants to remove a specific book from their favorites.
    *   Requires Parameter: `book_name` (string).
    *   Example Queries: "Remove 'The Great Gatsby' from favorites", "Unfavorite 'Dune'".
    *   JSON Output Template (Example):
        ```json
        { "action": "favourite_list", "operation": "remove", "parameters": { "book_name": "The Great Gatsby" } }
        ```

**2. Action Type: `reading_status`** (Interacting with the status of books: 'to_read', 'reading', 'completed')

*   **Operation: `show_summary`**
    *   Triggered by: User wants an overview of their reading status (counts for each category).
    *   Example Queries: "What's my reading status?", "Show my reading progress summary"
    *   JSON Output Template:
        ```json
        { "action": "reading_status", "operation": "show_summary", "parameters": {} }
        ```
*   **Operation: `show_specific_status`**
    *   Triggered by: User wants to see the list of books within a specific reading status category.
    *   Requires Parameter: `status` (string - must be one of: `"to_read"`, `"reading"`, `"completed"`).
    *   Example Queries: "Show me the books I am currently reading", "What books have I completed?", "List the books I want to read."
    *   JSON Output Template (Example for 'reading'):
        ```json
        { "action": "reading_status", "operation": "show_specific_status", "parameters": { "status": "reading" } }
        ```
    *   JSON Output Template (Example for 'completed'):
        ```json
        { "action": "reading_status", "operation": "show_specific_status", "parameters": { "status": "completed" } }
        ```
    *   JSON Output Template (Example for 'to_read'):
        ```json
        { "action": "reading_status", "operation": "show_specific_status", "parameters": { "status": "to_read" } }
        ```
*   **Operation: `set_status`**
    *   Triggered by: User wants to assign or change the reading status of a specific book.
    *   Requires Parameters: `book_name` (string), `status` (string: `"to_read"`, `"reading"`, `"completed"`).
    *   Example Queries: "Mark 'Dune' as currently reading", "Move '1984' to completed", "I want to read 'Sapiens'".
    *   JSON Output Template (Example):
        ```json
        { "action": "reading_status", "operation": "set_status", "parameters": { "book_name": "Dune", "status": "reading" } }
        ```
*   **Operation: `remove`**
    *   Triggered by: User wants to remove any reading status associated with a specific book.
    *   Requires Parameter: `book_name` (string).
    *   Example Queries: "Remove the reading status for 'Dune'", "Clear the status of '1984'".
    *   JSON Output Template (Example):
        ```json
        { "action": "reading_status", "operation": "remove", "parameters": { "book_name": "Dune" } }
        ```

**Handling Multiple Requests Examples:**

*   User Query: "Show my favorites and tell me how many there are."
*   Expected JSON Array Output:
    ```json
    [
        { "action": "favourite_list", "operation": "show_all", "parameters": {} },
        { "action": "favourite_list", "operation": "count", "parameters": {} }
    ]
    ```
*   User Query: "What am I reading and what have I completed?"
*   Expected JSON Array Output:
    ```json
    [
        { "action": "reading_status", "operation": "show_specific_status", "parameters": { "status": "reading" } },
        { "action": "reading_status", "operation": "show_specific_status", "parameters": { "status": "completed" } }
    ]
    ```
*   User Query: "Add Dune to favorites and mark it as reading."
*   Expected JSON Array Output:
    ```json
    [
        { "action": "favourite_list", "operation": "add", "parameters": { "book_name": "Dune" } },
        { "action": "reading_status", "operation": "set_status", "parameters": { "book_name": "Dune", "status": "reading" } }
    ]
    ```

**Remember: Analyze the ENTIRE user query. Respond ONLY with the appropriate single JSON object OR a JSON array containing the relevant objects, based on these instructions.**

---

**User Query:**

"""
    full_prompt = system_prompt + user_query
    return full_prompt


def get_gemini_instructions_internal(user_query):
    if not model:
        raise Exception("AI model not available.")

    full_prompt = get_full_prompt(user_query)
    try:
        response = model.generate_content(full_prompt)

        print("-" * 20)
        print(f"RAW GEMINI (Instructions) RESPONSE for query '{user_query}':")
        try:
            print(response.text)
        except Exception as print_err:
             print(f"[Error printing response text: {print_err}]")
        if hasattr(response, 'prompt_feedback'):
             print(f"Prompt Feedback: {response.prompt_feedback}")
        print("-" * 20)

        response_text = response.text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        if not response_text:
             raise ValueError("AI returned an empty response after cleanup.")

        instructions = json.loads(response_text)
        return instructions

    except json.JSONDecodeError as json_err:
        raise ValueError(f"Could not understand the AI's response format. Raw text was: '{response_text}'") from json_err
    except Exception as e:
        if hasattr(response, 'prompt_feedback'):
             print(f"Gemini Error - Prompt Feedback: {response.prompt_feedback}")
        raise ConnectionError(f"An error occurred communicating with the AI model: {e}") from e


def execute_single_action(instruction, current_user):
    action = instruction.get("action")
    operation = instruction.get("operation")
    parameters = instruction.get("parameters", {})
    book_name = parameters.get("book_name")
    status_value = parameters.get("status")

    def find_book(name):
        if not name:
            return None, {'status': 'error', 'message': 'Book name not specified.'}
        try:
            book = Book.objects.get(name__iexact=name)
            return book, None
        except Book.DoesNotExist:
            return None, {'status': 'error', 'message': f"Sorry, I couldn't find a book exactly named '{name}'."}
        except Book.MultipleObjectsReturned:
             # Find potential matches to suggest
             possible_matches = Book.objects.filter(name__icontains=name)[:5] # Limit results
             match_names = [b.name for b in possible_matches]
             return None, {'status': 'error', 'message': f"Multiple books match '{name}'. Could you mean one of these: {', '.join(match_names)}?"}

    if action == "favourite_list":
        if operation == "show_all":
            favorites = Favorite.objects.filter(user=current_user).select_related('book', 'book__authors')
            fav_list = [
                {"id": f.book.id,
                 "name": f.book.name,
                 "author": f.book.authors.name if f.book.authors else 'N/A',
                 "book_cover": f.book.image.url if f.book.image else 'N/A'
                 }
                for f in favorites
            ]
            count = len(fav_list)
            msg = f"Found {count} favorite book{'s' if count != 1 else ''}." if count > 0 else "You don't have any favorite books yet."
            return {'status': 'success', 'message': msg, 'data': fav_list}

        elif operation == "count":
            count = Favorite.objects.filter(user=current_user).count()
            msg = f"You have {count} favorite book{'s' if count != 1 else ''}."
            return {'status': 'success', 'message': msg, 'data': {'count': count}}

        elif operation == "add":
            book, error_response = find_book(book_name)
            if error_response: return error_response
            fav, created = Favorite.objects.get_or_create(user=current_user, book=book)
            msg = f"Okay, I've added '{book.name}' to your favorites." if created else f"'{book.name}' is already in your favorites."
            return {'status': 'success', 'message': msg, 'data': {'created': created, 'book_name': book.name}}

        elif operation == "remove":
            book, error_response = find_book(book_name)
            if error_response: return error_response
            num_deleted, _ = Favorite.objects.filter(user=current_user, book=book).delete()
            msg = f"Removed '{book.name}' from your favorites." if num_deleted > 0 else f"Couldn't find '{book.name}' in your favorites to remove."
            return {'status': 'success', 'message': msg, 'data': {'deleted_count': num_deleted > 0, 'book_name': book.name}}

    elif action == "reading_status":
        valid_statuses = ['to_read', 'reading', 'completed']
        status_map_display = {'to_read': 'Want to Read', 'reading': 'Currently Reading', 'completed': 'Completed'}

        if operation == "show_summary":
            status_counts = ReadingStatus.objects.filter(user=current_user)\
                              .values('status')\
                              .annotate(count=Count('id'))
            summary = {s: 0 for s in valid_statuses}
            for item in status_counts:
                summary[item['status']] = item['count']

            msg = "Here's a summary of your reading status:"
            return {'status': 'success', 'message': msg, 'data': summary}

        elif operation == "show_specific_status":
            if status_value not in valid_statuses:
                return {'status': 'error', 'message': f"Invalid status '{status_value}'. Please use 'to_read', 'reading', or 'completed'."}

            statuses = ReadingStatus.objects.filter(user=current_user, status=status_value)\
                         .select_related('book', 'book__authors')
            book_list = [
                {"id": s.book.id,
                 "name": s.book.name,
                 "author": s.book.authors.name if s.book.authors else 'N/A',
                 "book_cover": s.book.image.url if s.book.image else 'N/A'}
                for s in statuses
            ]
            count = len(book_list)
            status_display = status_map_display.get(status_value, status_value)
            if count > 0:
                 msg = f"Found {count} book{'s' if count != 1 else ''} marked as '{status_display}'."
            else:
                 msg = f"You haven't marked any books as '{status_display}' yet."
            return {'status': 'success', 'message': msg, 'data': book_list}

        elif operation == "set_status":
            book, error_response = find_book(book_name)
            if error_response: return error_response
            if status_value not in valid_statuses:
                return {'status': 'error', 'message': f"Invalid target status '{status_value}'. Please use 'to_read', 'reading', or 'completed'."}

            try:
                with transaction.atomic():
                    obj, created = ReadingStatus.objects.update_or_create(
                        user=current_user, book=book, defaults={'status': status_value}
                    )
                action_str = "marked" if created else "updated"
                status_display = status_map_display.get(status_value, status_value)
                msg = f"Okay, I've {action_str} '{book.name}' as '{status_display}'."
                return {'status': 'success', 'message': msg, 'data': {'created': created, 'book_name': book.name, 'status': status_value}}
            except Exception as db_err:
                print(f"DB Error setting status for {book.name}: {db_err}")
                return {'status': 'error', 'message': f"A database error occurred while setting status for '{book.name}'."}


        elif operation == "remove":
            book, error_response = find_book(book_name)
            if error_response: return error_response
            try:
                with transaction.atomic():
                     num_deleted, _ = ReadingStatus.objects.filter(user=current_user, book=book).delete()
                msg = f"Removed the reading status for '{book.name}'." if num_deleted > 0 else f"No reading status was set for '{book.name}'."
                return {'status': 'success', 'message': msg, 'data': {'deleted_count': num_deleted > 0, 'book_name': book.name}}
            except Exception as db_err:
                 print(f"DB Error removing status for {book.name}: {db_err}")
                 return {'status': 'error', 'message': f"A database error occurred while removing status for '{book.name}'."}


    elif action == "unknown":
        query_part = parameters.get("original_query_part", "part of your request")
        return {'status': 'warning', 'message': f"Sorry, I wasn't sure how to handle '{query_part}'. Could you try rephrasing?"}
    else:
        return {'status': 'error', 'message': f"An internal error occurred: Action '{action}/{operation}' is not supported by the system."}


def summarize_results_with_gemini(results: list, original_query: str) -> str:
    """
    Takes the list of action results and generates a user-friendly summary using Gemini.
    """
    if not summary_model:
        return "Processing is complete, but the summary generation AI is unavailable."

    if not results:
        return "It seems no specific actions were taken based on your request."

    results = [r for r in results if r is not None]
    if not results:
        return "It seems no specific actions were taken based on your request."

    all_unknown_or_warning = all(r.get('status') in ['warning', 'error'] and 'understand' in r.get('message', '').lower() for r in results)
    if all_unknown_or_warning:
        messages = [r.get('message') for r in results if r.get('message')]
        if messages:
             return " ".join(messages)
        else:
             return "Sorry, I had trouble understanding your request. Could you please rephrase?"

    summary_prompt = f"""
You are a friendly AI assistant summarizing the results of book library management actions for a user.
You will receive a JSON array representing the outcomes of actions taken based on the user's request: "{original_query}"

do not send json file use natural hunan language in a freandly way and hilight the book name
formate this message in a good way
also if there is "book_cover" in the json file wrap it with img tag and also add a <br> before the img tag
example: <br><img src="book_cover_link" class="botImage" height="150px">
and place the image of the book name

Now, summarize the following results:
{json.dumps(results, indent=2)}
"""

    try:
        response = summary_model.generate_content(summary_prompt)

        print("-" * 20)
        print(f"RAW GEMINI (Summary) RESPONSE for query '{original_query}':")
        try:
             print(response.text)
        except Exception as print_err:
             print(f"[Error printing response text: {print_err}]")
        if hasattr(response, 'prompt_feedback'):
             print(f"Prompt Feedback: {response.prompt_feedback}")
        print("-" * 20)

        if response.prompt_feedback.block_reason:
             print(f"Warning: Summary generation blocked. Reason: {response.prompt_feedback.block_reason}")
             return f"I've processed your request (Status: {results[0].get('status', 'unknown') if results else 'unknown'}), but I encountered an issue generating the final summary."

        summary_text = response.text.strip()
        return summary_text

    except Exception as e:
        print(f"ERROR during Gemini summary generation: {e}")
        traceback.print_exc()
        fallback_summary = "Here's a summary of the actions:\n"
        for res in results:
            status = res.get('status', 'Unknown').capitalize()
            message = res.get('message', 'No details.')
            fallback_summary += f"- {status}: {message}\n"
        return fallback_summary

def format_sse(event_type: str, data: dict) -> str:
    json_data = json.dumps(data)
    return f"event: {event_type}\ndata: {json_data}\n\n"


def _stream_nlp_processing(current_user, user_query):
    results = []
    overall_status = 'success'

    try:
        yield format_sse("status", {"message": "Received request, figuring out what you mean..."})
        time.sleep(0.5)

        try:
            instructions = get_gemini_instructions_internal(user_query)
            yield format_sse("status", {"message": "Okay, I understand. Processing your request..."})
            time.sleep(0.5)
        except (ValueError, ConnectionError, Exception) as gemini_err:
            print(f"GEMINI INSTRUCTION ERROR: {gemini_err}")
            error_message = f"Sorry, I had trouble understanding that. Could you try rephrasing? (Error: {gemini_err})"
            results.append({"status": "error", "message": error_message})
            overall_status = 'error'
            instructions = []


        instruction_list = []
        if isinstance(instructions, list):
            instruction_list = instructions
            if not instruction_list and overall_status == 'success':
                 yield format_sse("warning", {"message": "AI interpretation resulted in no specific actions."})
                 results.append({'status': 'warning', 'message': "I couldn't identify any specific actions in your request."})
                 overall_status = 'warning'
            elif instruction_list:
                 yield format_sse("status", {"message": f"Performing {len(instruction_list)} action{'s' if len(instruction_list) != 1 else ''}..."})
                 time.sleep(0.2)
        elif isinstance(instructions, dict):
            instruction_list = [instructions]
            yield format_sse("status", {"message": "Performing 1 action..."})
            time.sleep(0.2)
        elif overall_status != 'error':
            yield format_sse("error", {"message": "Received unexpected instruction format from AI."})
            results.append({'status': 'error', 'message': "Internal error: Invalid format received from AI."})
            overall_status = 'error'


        action_index = 0
        for instruction in instruction_list:
             action_index += 1
             if isinstance(instruction, dict):
                 action_desc = f"{instruction.get('action', 'N/A')}/{instruction.get('operation', 'N/A')}"
                 try:
                     result = execute_single_action(instruction, current_user)
                     results.append(result)

                     if result.get('status') == 'error':
                         overall_status = 'error' if overall_status == 'error' else 'partial_success'
                         yield format_sse("warning", {"message": f"Issue with action {action_index}: {result.get('message')}"})
                     elif result.get('status') == 'warning':
                         if overall_status == 'success':
                             overall_status = 'warning'
                         yield format_sse("warning", {"message": f"Note for action {action_index}: {result.get('message')}"})
                     else:
                        pass

                     time.sleep(0.3)

                 except Exception as exec_err:
                     print(f"ERROR during action execution {action_index} ({action_desc}): {exec_err}")
                     traceback.print_exc()
                     error_msg = f"A server error occurred while trying to '{action_desc}'."
                     results.append({'status': 'error', 'message': error_msg})
                     overall_status = 'error' # Critical failure
                     yield format_sse("error", {"message": error_msg})

             else:
                 error_msg = f"Invalid instruction format found at step {action_index}."
                 results.append({'status': 'error', 'message': error_msg})
                 overall_status = 'error'
                 yield format_sse("error", {"message": error_msg})


    except Exception as e:
        print(f"FATAL STREAM ERROR in _stream_nlp_processing: {e}")
        traceback.print_exc()
        overall_status = 'error'
        if not any(r.get('status') == 'error' for r in results):
             results.append({'status': 'error', 'message': 'A critical server error occurred during processing.'})
        yield format_sse("error", {"message": f"A critical server error occurred: {e}"})


    yield format_sse("status", {"message": "Wrapping up..."})
    time.sleep(0.5)

    final_summary = "Processing completed."
    try:
        final_summary = summarize_results_with_gemini(results, user_query)
    except Exception as summary_err:
        print(f"ERROR calling summary function: {summary_err}")
        traceback.print_exc()
        fallback_summary = f"Finished processing with status: {overall_status}.\n"
        if results:
             fallback_summary += "Details:\n"
             for res in results:
                 fallback_summary += f"- {res.get('status', 'N/A').capitalize()}: {res.get('message', 'No message.')}\n"
        final_summary = fallback_summary


    final_data = {
        "status": overall_status,
        "summary_message": final_summary
    }
    yield format_sse("finished", final_data)


@login_required
def agent_chat_page(request):
    now = datetime.now()
    formatted_time = now.strftime('%I:%M:%S %p')
    return render(request, 'homePage/ai_agent.html', {'time': formatted_time})


@login_required
@require_POST
def initiate_nlp_processing(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            user_query = data.get('query')
        else:
            user_query = request.POST.get('prompt')

        if not user_query:
            return JsonResponse({'status': 'error', 'message': 'Query parameter missing.'}, status=400)

        stream_id = uuid.uuid4()

        session_key = f'nlp_query_{stream_id}'
        request.session[session_key] = user_query
        request.session.set_expiry(600)


        return JsonResponse({'status': 'success', 'stream_id': str(stream_id)})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        print(f"Error in initiate_nlp_processing: {e}")
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': 'Server error during initiation.'}, status=500)




@login_required
@require_GET
def stream_nlp_results(request, stream_id):
    session_key = f'nlp_query_{stream_id}'
    user_query = request.session.pop(session_key, None)

    if user_query is None:
        print(f"Error: Query not found in session for stream ID {stream_id}")
        def error_stream():
            yield format_sse("error", {"message": "Session expired or link invalid. Please try sending your request again."})
            yield format_sse("finished", {"status": "error", "summary_message": "Could not process request due to an invalid session. Please try again."})

        response = StreamingHttpResponse(error_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    response = StreamingHttpResponse(
        _stream_nlp_processing(request.user, user_query),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
