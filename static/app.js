const button = document.getElementById("new-quote-btn");
const quoteText = document.getElementById("quote-text");
const quoteAuthor = document.getElementById("quote-author");
const historyList = document.getElementById("history-list");

function renderHistoryItem(quote, author) {
  const li = document.createElement("li");
  li.innerHTML = `<blockquote>${quote}</blockquote><span>— ${author}</span>`;
  return li;
}

button.addEventListener("click", async () => {
  button.disabled = true;
  button.textContent = "Loading...";

  try {
    const response = await fetch("/api/quote");
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to fetch quote.");
    }

    quoteText.textContent = `“${data.quote}”`;
    quoteAuthor.textContent = `— ${data.author}`;

    const empty = historyList.querySelector(".empty-history");
    if (empty) empty.remove();

    historyList.prepend(renderHistoryItem(data.quote, data.author));
  } catch (error) {
    quoteText.textContent = error.message;
    quoteAuthor.textContent = "";
  } finally {
    button.disabled = false;
    button.textContent = "New Quote";
  }
});
