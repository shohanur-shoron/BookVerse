function habijabi(){
    const paragraph = document.querySelector("#rightText p");
    const propmt = document.querySelector("#leftText p");
    let propmtText = document.getElementById('inputText');

    propmt.textContent = propmtText.value;
    propmtText.value = "";


    let text = `Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eaque voluptatem doloribus iusto hic! Quibusdam, asperiores porro. Tempore nemo alias obcaecati dignissimos libero pariatur non enim debitis, iure aut est culpa amet, consequatur sed vero nostrum laborum quasi nam eveniet provident minima atque! Odit, esse cumque voluptas, dolorem eligendi commodi voluptate recusandae fugiat aut temporibus praesentium dicta! Soluta, consequatur omnis enim odio quidem eveniet eligendi nostrum corporis veniam pariatur aspernatur tempora iure, cupiditate quam, cum illum voluptas. Incidunt veritatis, rerum nam autem mollitia perferendis, iste earum ducimus laboriosam saepe dolorem! Labore aliquam soluta, maiores reprehenderit distinctio odit consequatur molestias autem blanditiis!Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eaque voluptatem doloribus iusto hic! Quibusdam, asperiores porro. Tempore nemo alias obcaecati dignissimos libero pariatur non enim debitis, iure aut est culpa amet, consequatur sed vero nostrum laborum quasi nam eveniet provident minima atque! Odit, esse cumque voluptas, dolorem eligendi commodi voluptate recusandae fugiat aut temporibus praesentium dicta! Soluta, consequatur omnis enim odio quidem eveniet eligendi nostrum corporis veniam pariatur aspernatur tempora iure, cupiditate quam, cum illum voluptas. Incidunt veritatis, rerum nam autem mollitia perferendis, iste earum ducimus laboriosam saepe dolorem! Labore aliquam soluta, maiores reprehenderit distinctio odit consequatur molestias autem blanditiis!Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eaque voluptatem doloribus iusto hic! Quibusdam, asperiores porro. Tempore nemo alias obcaecati dignissimos libero pariatur non enim debitis, iure aut est culpa amet, consequatur sed vero nostrum laborum quasi nam eveniet provident minima atque! Odit, esse cumque voluptas, dolorem eligendi commodi voluptate recusandae fugiat aut temporibus praesentium dicta! Soluta, consequatur omnis enim odio quidem eveniet eligendi nostrum corporis veniam pariatur aspernatur tempora iure, cupiditate quam, cum illum voluptas. Incidunt veritatis, rerum nam autem mollitia perferendis, iste earum ducimus laboriosam saepe dolorem! Labore aliquam soluta, maiores reprehenderit distinctio odit consequatur molestias autem blanditiis!`;
    let wordsArray = text.split(" ");


    let index = 0;
    let output = ""; // To store the streamed text
    let displayElement = document.getElementById("output"); // Ensure this element exists in HTML

    let interval = setInterval(() => {
        if (index < wordsArray.length) {
            output += wordsArray[index] + " "; // Add the next word with a space
            displayElement.textContent = output; // Update the display
            index++; 
        } else {
            clearInterval(interval); // Stop when all words are added
        }
    }, 80);
}

