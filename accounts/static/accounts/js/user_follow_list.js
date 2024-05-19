const followToggleBtn = document.querySelectorAll(".follow-toggle-list-btn");

followToggleBtn.forEach((button) => {
  button.addEventListener("click", async function () {
    const userId = this.dataset.userId;
    const form = document.querySelector(`#follow-toggle-list-form-${userId}`);
    const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;
    const messagesDiv = document.getElementById("messages");

    const response = await fetch(form.action, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      console.error("Failed to toggle follow status.");
    }

    const data = await response.json();
    if (data.success) {
      // // Update the messages div with the flash message
      const alertDiv = document.createElement("div");
      alertDiv.className = "alert alert-success alert-dismissible fade show";
      alertDiv.role = "alert";
      alertDiv.innerHTML = `
           ${data.message}
           <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
         `;
      messagesDiv.innerHTML = "";
      messagesDiv.appendChild(alertDiv);

      // Update the button text and class based on the follow state
      if (data.is_following) {
        this.textContent = "Following";
        this.classList.replace("btn-success", "btn-outline-success");
      } else {
        this.textContent = "Follow";
        this.classList.replace("btn-outline-success", "btn-success");
      }
    } else {
      console.error("Failed to toggle follow status.");
    }
  });
});
