function updateQuantity(cartId) {
    const quantity = document.getElementById(`quantity_${cartId}`).value;
    fetch(`/update_cart/${cartId}`, {
        method: 'POST',
        body: JSON.stringify({quantity: quantity}),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.json())
      .then(data => {
          if (data.status === 'success') {
              window.location.reload();
          } else {
              alert('Failed to update the cart.');
          }
      });
}

function removeFromCart(cartId) {
    fetch(`/remove_from_cart/${cartId}`, {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          if (data.status === 'success') {
              window.location.reload();
          } else {
              alert('Failed to remove the item from the cart.');
          }
      });
}

function checkout() {
    // Redirect to a checkout page or handle checkout logic
    alert('Checkout functionality needs to be implemented.');
}
