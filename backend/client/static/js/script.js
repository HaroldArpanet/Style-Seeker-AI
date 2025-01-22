const API_BASE_URL = SERVER_ADDRESS;
const productsContainer = document.getElementById('products-container');
const searchBox = document.getElementById('search-box');
const searchButton = document.getElementById('search-button');
const body = document.body;

function displayProducts(products, container) {
    container.innerHTML = '';
    products.forEach(product => {
        const productBox = document.createElement('div');
        productBox.className = 'product-box';
        productBox.innerHTML = `
            <img src="${product.images[0]}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>price: ${product.current_price}-${product.currency}</p>
            <p>${product.description.slice(0,35)}...</p>
        `;
        container.appendChild(productBox);
    });
}

async function fetchProducts(query, container) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/search/v1/product_search/search/?query=${query}`);
        const data = await response.json();
        displayProducts(data, container);
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

function switchToProductPage(query) {
    body.innerHTML = '';

    body.innerHTML = `
        <div id="logo">
            <h1>Style Seeker</h1>
        </div>
        <div id="chat-container">
            <div id="chat-panel">
                <div id="chat-history"></div>
                <div id="chat-input-container">
                    <input type="text" id="chat-input" placeholder="Type your message...">
                    <button id="send-button">Send</button>
                </div>
            </div>
            <div id="product-display"></div>
        </div>
        <div id="github-link">
            <a href="https://github.com/HaroldArpanet/Style-Seeker-AI/">
                <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub Logo">
            </a>
        </div>
    `;

    const chatHistory = document.getElementById('chat-history');
    const chatData = JSON.parse(localStorage.getItem('chatData')) || [];
    chatHistory.innerHTML = chatData.map(msg => `<div class="message">${msg.role}: ${msg.content}</div>`).join('');

    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const productDisplay = document.getElementById('product-display');

    async function sendMessage() {
        const userMessage = chatInput.value.trim();
        if (userMessage) {
            chatData.push({ role: 'user', content: userMessage });
            localStorage.setItem('chatData', JSON.stringify(chatData));
            chatHistory.innerHTML += `<div class="message">user: ${userMessage}</div>`;

            try {
                const response = await fetch('${API_BASE_URL}/api/llm_chat/v1/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        messages: [{ role: 'user', content: userMessage }],
                    }),
                });
                const data = await response.json();

                chatData.push({ role: 'assistant', content: data.assistant_response.content });
                localStorage.setItem('chatData', JSON.stringify(chatData));
                chatHistory.innerHTML += `<div class="message">assistant: ${data.assistant_response.content}</div>`;

                if (data.search_results) {
                    displayProducts(data.search_results, productDisplay);
                } else {
                    alert('Payment error');
                }
            } catch (error) {
                console.error('Error sending message:', error);
            }

            chatInput.value = '';
        }
    }

    sendButton.addEventListener('click', sendMessage);

    chatInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    chatHistory.scrollTop = chatHistory.scrollHeight;

    if (query) {
        fetchProducts(query, productDisplay);
    }
}

searchButton.addEventListener('click', () => {
    const query = searchBox.value.trim();
    if (query) {
        switchToProductPage(query);
    }
});

searchBox.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        const query = searchBox.value.trim();
        if (query) {
            switchToProductPage(query);
        }
    }
});

fetchProducts('dress', productsContainer);