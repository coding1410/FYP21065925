function filterProducts() {
    const searchInput = document.getElementById('searchBar').value.toLowerCase();
    let productContainers = document.querySelectorAll('.product');

    productContainers.forEach(function(product) {
        const productName = product.querySelector('h4').textContent.toLowerCase();
        if (productName.includes(searchInput)) {
            product.style.display = '';
        } else {
            product.style.display = 'none';
        }
    });
}

function sortProducts() {
    let productsWrapper = document.querySelector('.products');
    let products = Array.from(productsWrapper.children);
    const sortOption = document.getElementById('sortPrice').value;

    products.sort((a, b) => {
        const priceA = parseFloat(a.getAttribute('data-price'));
        const priceB = parseFloat(b.getAttribute('data-price'));

        if (sortOption === 'asc') {
            return priceA - priceB;
        } else {
            return priceB - priceA;
        }
    });

    // Re-append products in sorted order
    products.forEach(product => productsWrapper.appendChild(product));
}

function addToCart(productId) {
    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `product_id=${productId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Product added to cart successfully!');
            // Optionally update cart display or quantity here
        } else {
            alert('Failed to add product to cart. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
