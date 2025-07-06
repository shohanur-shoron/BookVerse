// --- START OF FILE gemini2.js ---

import { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } from "https://cdn.jsdelivr.net/npm/@google/generative-ai/+esm";

// --- Configuration ---
// WARNING: Storing API keys client-side is insecure for production. Use a backend proxy.
const API_KEY = "API Key";
// const MODEL_NAME = "gemini-1.5-pro";
const MODEL_NAME = "gemini-2.0-flash";


// --- Fixed Book Category List ---
const bookCategoryList = `
- Islamic Books: Books focusing on Islam, including the Quran, Hadith, and religious teachings.
- Novel: Fictional stories with a focus on character development and engaging narratives.
- Computer: Books covering technology, software, hardware, and computer science topics.
- Freelancing: Guides on freelance work, including client management and skill development.
- Programming: Books about coding, software development, and programming languages.
- Biographies: Real-life stories highlighting the achievements and experiences of individuals.
- Memoirs and Interviews: Personal life stories and collections of discussions with notable figures.
- Children's Books: Stories and educational content designed for young readers.
- Science Fiction: Books exploring futuristic technology, space, aliens, and speculative themes.
- Admission: Guides for school or college admission processes, including test preparation.
- Recruitment: Books on hiring strategies, job search techniques, and career development.
- Preparatory Examination: Study guides, practice tests, and tips for exam preparation.
- Story: Fictional narratives across various genres and themes.
- Self Development: Books focused on personal growth and self-improvement.
- Motivational: Uplifting content to inspire and encourage readers.
- Meditation: Guides on mindfulness, relaxation, and meditation techniques.
- Translation: Works translated from other languages for broader accessibility.
- Mathematics: Books covering mathematical concepts, theories, and problems.
- Science: Content on scientific principles, discoveries, and research.
- Technology: Books about tech advancements, applications, and innovations.
- Mystery: Stories with suspense, puzzles, and intriguing plots
- Detective: Books featuring investigations, crime-solving, and detective work.
- Horror: Chilling tales designed to scare and thrill readers.
- Thriller: Suspense, crime, high stakes, fast-paced plots.
- Adventure: Exploration, quests, bravery, exotic settings.
- Politics: Government, political theories, current affairs, political figures.
- History: Past events, cultures, civilizations, historical figures.
- Tradition: Cultural customs, traditional arts, ways of life.
- Business: Management, entrepreneurship, marketing, finance.
- Investment: Investment strategies, financial markets, personal finance.
- Economics: Economic theories, systems, policies, economic issues.
- Language: Linguistics, language learning, grammar, communication.
- Dictionary: Word definitions, pronunciations, etymologies.
- Travel: Destination guides, travelogues, cultural insights.
- Immigration: Immigrant experiences, policies, social and economic impacts.
- Liberation: Liberation movements, struggles for freedom, concepts of liberation.
- War: Historical accounts, military strategy, soldier memoirs, wartime stories.
- Law and Justice: Explores legal systems, crime, justice mechanisms, and the roles of legal professions.
- English Language: Focuses on grammar, vocabulary, language learning, and effective communication skills.
- University: Covers higher education, campus life, academic subjects, and student experiences.
- Engineering: Delves into technology, design, and innovation across fields like civil, mechanical, and electrical engineering.
- Comics: Highlights graphic novels, comic books, visual storytelling, and popular characters.
- Design: Examines visual arts, aesthetics, creativity, and functionality across various mediums.
- Photography: Discusses image capture, techniques, artistic expression, and photojournalism.
- Agriculture: Addresses farming, food production, cultivation methods, and sustainability practices.
- Farmers: Looks at the lives of farmers, agricultural communities, and farming practices.
- Media: Investigates communication, information dissemination, media platforms, and their societal impact.
- Journalism: Focuses on news reporting, investigative journalism, storytelling, and media ethics.
- Copperplate: Explores a calligraphy style, historical scripts, engraving, and artistic writing.
- Systec Publications: Books from a specific publisher, focusing on their typical content.
- Readers' Gathering: Books that foster community reading or discussion, often for book clubs.
- Rhymes: Collections of rhyming poetry or children's rhymes.
- Poems: Books of poetry covering various styles and themes.
- Recitations: Works intended for public reading or performance, like poetry or prose.
- Drawing: Books on drawing techniques or showcasing art.
- Painting Design: Explores painting art, design principles, or painted designs.
- Drama Book: Contains plays or scripts for theatrical performances.
- Family: Focuses on family dynamics, relationships, or family-centered stories.
- Child Affairs: Addresses children's issues, rights, or perspectives.
- Parenting: Offers advice, strategies, or stories on raising children.
- Award Winning Book: Recognized literary works across genres that have received awards.
- Professional: Books focused on career development, industry-specific skills, or professional growth, such as guides on leadership, project management, or technical expertise.
- Journal: Books designed for personal or professional journaling, often containing prompts or blank pages for reflective or creative writing.
- Reference: Quick-access books like dictionaries, encyclopedias, or manuals, providing factual information on specific topics for easy lookup.
- Essay: Collections of essays exploring diverse topics, such as literature, philosophy, social issues, or personal reflections.
- Bangladesh: Books covering Bangladesh’s history, culture, politics, or literature, including travel guides, memoirs, or academic studies.
- Medical: Books on health, medical practices, diseases, or healthcare systems, including textbooks, patient guides, or wellness advice.
- Cooking: Books featuring recipes, cooking techniques, or culinary traditions, often focused on specific cuisines or dietary preferences.
- Food: Books exploring food culture, history, science, or global cuisines, such as studies on food trends or the impact of food on society.
- Nutrition: Books focused on dietary health, nutrition science, or diet planning, including guides on balanced eating or managing specific health conditions.
- Music: Books covering music theory, history, biographies of musicians, or specific genres, such as classical, jazz, or modern music.
- Movies: Books on film history, criticism, industry insights, or iconic films, including analyses of cinematography, director biographies, or movie trivia.
- Entertainment: Books focused on amusement, including celebrity stories, games, or pop culture topics.
- Society: Explores social structures, norms, issues, or community dynamics.
- Civilization: Covers the development, achievements, or decline of human civilizations.
- Culture: Highlights traditions, arts, beliefs, or lifestyles of specific groups.
- Books for Schools: Educational content or stories tailored for school-aged children.
- Books for College: Academic texts, guides, or narratives for college students.
- Books for Madrasas: Religious or educational books for Islamic learning institutions.
- Health: Books on overall well-being, disease prevention, or healthy living.
- Care: Focuses on caregiving, patient support, or self-care practices.
- Treatment: Covers medical treatments, therapies, or healing methods.
- Fitness: Guides on exercise, strength training, or physical wellness.
`;

// --- System Prompt for Guiding the AI ---
const systemPrompt = `
You are a friendly and helpful book assistant. Your primary goal is to analyze the user's description of their interests and recommend relevant book categories from a fixed list. **Your secondary goal, ONLY IF the user explicitly asks for book examples within a specific category, is to provide a few relevant example titles.**

**CORE TASK 1: Category Recommendation (Default Task)**

**RULES:**
1.  **Use ONLY categories from this fixed list for initial recommendations:**
    ${bookCategoryList}
2.  **Analyze the user's input:** Understand the core themes and topics the user enjoys reading about for the initial category suggestion.
3.  **Recommend & Explain Categories:** Identify 1-4 of the MOST relevant categories from the list based on the user's input.
4.  **Category Output Format:**
    *   Respond in a friendly, conversational, and helpful tone.
    *   Briefly explain *why* you are recommending each category, connecting it directly to the user's stated interests.
    *   Clearly present the recommended category name(s) from the list. Use Markdown bolding for the category names (e.g., "**Category Name**").
    *   Do NOT invent categories or use names not exactly matching the list for the initial recommendation.
    *   Keep the explanation concise (usually 1-2 sentences per recommended category is enough).
    *   Structure the response naturally. Start with a friendly acknowledgment if appropriate.
    *   Conclude your category recommendation response with a brief, friendly closing sentence. (e.g., "I hope this helps you find some great books!", "Happy reading!").

**CORE TASK 2: Book Examples (Activated ONLY by Explicit User Request)**

**RULES:**
5.  **Handle Book Requests:** **Crucially, IF AND ONLY IF the user explicitly asks for book examples, titles, or suggestions *within a specific category* (e.g., "Suggest some History books," "Give me examples from Science Fiction," "What are some good Thriller titles?"), you MUST switch from recommending categories to providing example titles.**
    *   Acknowledge the category they are asking about.
    *   **DO NOT simply repeat the category name or description.**
    *   Provide 3-5 relevant *example* book titles that fit the category.
    *   Clearly state that these are just *examples* or *suggestions*. You do not have access to a real-time book database or inventory.
    *   List the example titles, preferably using bullet points.
    *   You can invent plausible-sounding titles or mention well-known examples relevant to the category if appropriate based on your training data.
    *   Conclude with a friendly closing remark.
6.  **Stay On Topic / Refusal:**
    *   If the user asks about anything NOT related to describing their reading interests OR asking for book examples *within a specific category from the list*, you MUST refuse politely.
    *   Respond ONLY with: "I'm here to help you find book categories based on your interests or suggest some book examples within those categories! Could you tell me more about the kinds of topics you enjoy, or ask for examples from a specific category?" Do not answer unrelated questions.

**Example Interaction 1 (Category Finding):**
*   User Input: "I love reading about spaceships, aliens, and future worlds."
*   Your Correct Output: "That sounds exciting! Based on your interest in spaceships, aliens, and future worlds, the **Science Fiction** category seems like a perfect fit. It explores exactly those kinds of futuristic and speculative themes. Happy exploring those future worlds!"

**Example Interaction 2 (Asking for Book Examples - CORRECT TRANSITION):**
*   User Input (Following Interaction 1): "Okay, can you suggest some specific book *titles* in the **Science Fiction** category?"
*   Your Correct Output: "Sure! For the **Science Fiction** category, here are a few examples of the types of books you might find:\n\n*   *Dune* by Frank Herbert (A classic epic of politics and survival on a desert planet)\n*   *The Martian* by Andy Weir (A realistic story of survival on Mars)\n*   *Foundation* by Isaac Asimov (A galaxy-spanning tale of predicting the future)\n*   *Project Hail Mary* by Andy Weir (A lone astronaut on a mission to save Earth)\n\nThese are just a few suggestions to get you started in that category. Happy reading!"

**Example Interaction 3 (Category Finding):**
*   User Input: "I'm looking for books that transport me to another time and place. I love historical fiction, especially set in Victorian England or Ancient Rome."
*   Your Correct Output: "That sounds wonderful! Based on your love for historical fiction set in specific eras like Victorian England or Ancient Rome, I recommend these categories:\n\n*   **History**: Provides factual background and context for the eras you enjoy.\n*   **Novel**: Many historical fiction works fall under this broad category, focusing on narrative and character within a historical setting.\n*   **Tradition**: Might capture books focusing on the social customs and daily life aspects you mentioned.\n\nI hope these suggestions help you discover some captivating historical reads!"

**Example Interaction 4 (Asking for Book Examples - CORRECT TRANSITION):**
*   User Input (Following Interaction 3): "ok now suggest me some History book titles"
*   Your Correct Output: "Certainly! For the **History** category, focusing on periods like Ancient Rome or Victorian England, here are a few *examples* of the kinds of books you might explore:\n\n*   *SPQR: A History of Ancient Rome* by Mary Beard (A comprehensive look at Roman history)\n*   *Rubicon: The Last Years of the Roman Republic* by Tom Holland (Focuses on a pivotal period)\n*   *How to Be a Victorian* by Ruth Goodman (Explores the daily life details of the Victorian era)\n*   *The Victorian City: Everyday Life in Dickens' London* by Judith Flanders (Dives into the specifics of Victorian urban life)\n\nRemember, these are just examples to give you an idea of what's available in the History category. Enjoy your journey into the past!"

**Example Interaction 5 (Off-Topic Refusal):**
*   User Input: "What's the weather like today?"
*   Your Correct Output: "I'm here to help you find book categories based on your interests or suggest some book examples within those categories! Could you tell me more about the kinds of topics you enjoy, or ask for examples from a specific category?"

Now, analyze the following user input and respond according to these rules.
`;


// --- Conversation History (Optional for this specific task, but kept for structure) ---
// Note: For this focused task, we might not strictly need history,
// as the system prompt guides each interaction independently.
let chatHistory = [];
console.log("Initial chat history:", chatHistory);

// --- Initialize Gemini ---
let genAI;
let model;
try {
    genAI = new GoogleGenerativeAI(API_KEY);
    model = genAI.getGenerativeModel({ model: MODEL_NAME });
    console.log("GoogleGenerativeAI initialized successfully.");
} catch (error) {
    console.error("Error initializing GoogleGenerativeAI:", error);
    alert("Failed to initialize the AI service. Please check the API key and configuration in gemini2.js");
}

// --- Safety Settings ---
// Keeping safety settings minimal or moderate is usually fine for this use case.
// You can uncomment and adjust if needed, but BLOCK_NONE is generally not recommended.
const safetySettings = [
    { category: HarmCategory.HARM_CATEGORY_HARASSMENT,         threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE },
    { category: HarmCategory.HARM_CATEGORY_HATE_SPEECH,        threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE },
    { category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE },
    { category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,  threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE },
];
// const safetySettings = []; // Use with caution if specific content needs are understood


// --- Generation Configuration ---
const generationConfig = {
    temperature: 0.6, // Increased slightly for more natural language (adjust 0.5-0.7 as needed)
    topK: 1,
    topP: 0.95,
    maxOutputTokens: 256, // Increased slightly to allow for explanations
};




/**
 * Sends the system prompt + new user prompt to the Gemini API
 * and streams the response (expected to be category names or refusal).
 * Updates history upon successful completion.
 *
 * @param {string} newPrompt - The user's latest message (their interests).
 * @param {HTMLElement} targetElement - The message element to update.
 * @param {object} callbacks - UI update callback functions.
 */
async function streamChatResponse(newPrompt, targetElement, callbacks) {
    if (!model) {
        const errorMsg = "AI Model is not initialized. Check API Key and console.";
        console.error(errorMsg);
        callbacks.onError(targetElement, errorMsg);
        callbacks.onComplete(targetElement); // Still complete UI flow
        return;
    }

    let fullResponse = "";
    let isFirstChunk = true;
    let streamHasData = false;

    // *** MODIFIED: Construct the input with the System Prompt ***
    // We combine the system instructions and the user's current query into one user turn.
    // For this task, sending the whole chatHistory might confuse the model,
    // so we send the instructions + current query each time.
    const messagesToSend = [
        {
            role: "user",
            parts: [{ text: systemPrompt + "\n\nUser's Interests:\n" + newPrompt }]
            // Note: We are NOT including the potentially long chatHistory here.
            // The systemPrompt provides all necessary context for *this specific task*.
        }
    ];

    console.log("Sending to Gemini (including system prompt):\n", messagesToSend[0].parts[0].text.substring(0, 500) + "..."); // Log start of prompt

    let result;
    try {
        console.log("Calling model.generateContentStream()...");
        result = await model.generateContentStream({
            contents: messagesToSend,
            generationConfig,
            safetySettings,
        });
        console.log("model.generateContentStream() call returned. Awaiting stream...");

        for await (const chunk of result.stream) {
            // console.log("Received stream chunk:", chunk); // Debugging

            // Immediate check for prompt feedback in the chunk itself (less common now)
            if (chunk.promptFeedback && chunk.promptFeedback.blockReason) {
                const blockMessage = `Blocked based on prompt (during stream): ${chunk.promptFeedback.blockReason}`;
                console.error(blockMessage);
                throw new Error(blockMessage);
            }

            const chunkText = chunk.text();
            // console.log("Extracted chunk text:", chunkText); // Debugging

            if (chunkText !== undefined && chunkText !== null) {
                if (chunkText.length > 0) {
                    streamHasData = true;
                    fullResponse += chunkText;
                    // **MODIFICATION**: Don't parse with Marked for this specific output.
                    // We expect plain text (category names or refusal message).
                    // If you *need* markdown elsewhere, conditionally apply it based on context.
                    // const parsedHtml = typeof marked !== 'undefined' ? marked.parse(fullResponse) : fullResponse;
                    const parsedHtml = typeof marked !== 'undefined' ? marked.parse(fullResponse) : fullResponse;
                    callbacks.onData(targetElement, parsedHtml, isFirstChunk);
                    isFirstChunk = false;
                }
            }
        }

        console.log("Finished iterating through stream.");

        // Check the final aggregated response object
        const finalResponse = await result.response;
        console.log("Final response object:", JSON.stringify(finalResponse, null, 2));

        const promptFeedback = finalResponse?.promptFeedback;
        const finishReason = finalResponse?.candidates?.[0]?.finishReason;
        const safetyRatings = finalResponse?.candidates?.[0]?.safetyRatings;

        // Check for blocks or unexpected finish reasons in the final response
        if (promptFeedback?.blockReason) {
            const blockMessage = `Request blocked by API. Reason: ${promptFeedback.blockReason}`;
            console.error(blockMessage);
            throw new Error(blockMessage);
        }

        if (finishReason && finishReason !== "STOP" && finishReason !== "MAX_TOKENS") {
             const reasonMessage = `Stream finished unexpectedly. Reason: ${finishReason}`;
             console.warn(reasonMessage, "Safety Ratings:", safetyRatings);
             if (finishReason === "SAFETY") {
                throw new Error("Response blocked by safety filters.");
             } else {
                 throw new Error(reasonMessage); // Other non-STOP reasons are errors here
             }
        }

        // Final check: Did we get any actual content?
        if (streamHasData) {
            console.log("Stream finished successfully with data. Updating history.");
            // Update history (optional, but can be useful for debugging UI)
            chatHistory.push({ role: "user", parts: [{ text: newPrompt }] }); // Store original user prompt
            chatHistory.push({ role: "model", parts: [{ text: fullResponse }] }); // Store AI response
            console.log("Updated History:", JSON.stringify(chatHistory.slice(-4))); // Log recent history
            callbacks.onComplete(targetElement);
        } else {
            // No stream data received, even if finishReason was STOP
            console.warn("Stream finished, but no text content was processed/received.");
             if (finishReason === "STOP") {
                 // This implies the model chose to generate nothing based on the prompt.
                 // Could be a refusal, or it genuinely couldn't find a category.
                 // Let's return a clearer message instead of a generic error.
                 callbacks.onError(targetElement, "The AI could not determine a suitable category or chose not to respond based on the input.");
                 callbacks.onComplete(targetElement); // Still complete UI flow
             } else {
                 // If reason wasn't STOP and no data, likely an underlying issue.
                 throw new Error("Received an empty response from the AI. (Reason Unknown)");
             }
        }

    } catch (error) {
        console.error("Error during Gemini stream processing:", error);
        callbacks.onError(targetElement, error.message || "An unknown error occurred while contacting the AI.");
        callbacks.onComplete(targetElement); // Ensure UI is re-enabled
    }
}

// Ensure the function is globally accessible for your other scripts (like scripts.js)
window.streamChatResponse = streamChatResponse;
console.log("streamChatResponse available on window?", typeof window.streamChatResponse === 'function');

// --- END OF FILE gemini2.js ---