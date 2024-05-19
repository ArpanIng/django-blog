const followToggleForm = document.getElementById("follow-toggle-form");
const followToggleBtn = document.getElementById("follow-toggle-btn");
const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
const messagesDiv = document.getElementById("messages");
const followersCountSpan = document.getElementById('followers-count');

followToggleBtn.addEventListener("click", async () => {
  try {
    const response = await fetch(followToggleForm.getAttribute("action"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({}),
    });

    if (response.ok) {
      const result = await response.json();
      if (result.success) {
        // Update the messages div with the flash message
        const alertDiv = document.createElement("div");
        alertDiv.className = "alert alert-success alert-dismissible fade show";
        alertDiv.role = "alert";
        alertDiv.innerHTML = `
            ${result.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        messagesDiv.innerHTML = "";
        messagesDiv.appendChild(alertDiv);

        // Update the button text and class based on the follow state
        if (result.is_following) {
          followToggleBtn.textContent = "Following";
          followToggleBtn.classList.remove("btn-success");
          followToggleBtn.classList.add("btn-outline-success");
        } else {
          followToggleBtn.textContent = "Follow";
          followToggleBtn.classList.remove("btn-outline-success");
          followToggleBtn.classList.add("btn-success");
        }

        // Update the follower count
        followersCountSpan.textContent = result.followers_count;
      } else {
        console.error("Failed to toggle follow status.");
      }
    } else {
      console.error("Failed to toggle follow status:", result.message);
    }
  } catch (error) {
    console.log("Error", error);
  }
});
