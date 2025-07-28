document.addEventListener('DOMContentLoaded', function() {
    const profilePicWrapper = document.getElementById('profile-picture-overlay');
    const profilePicUpload = document.getElementById('profile-pic-upload');
    const profileAvatarDisplay = document.getElementById('profile-avatar-display');

    // Trigger file input when overlay/camera icon is clicked
    profilePicWrapper.addEventListener('click', function() {
        profilePicUpload.click();
    });

    profilePicUpload.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                profileAvatarDisplay.src = e.target.result; // Display preview
            };
            reader.readAsDataURL(file);

            // --- Send the file to the server ---
            const formData = new FormData();
            formData.append('profile_picture', file);

            fetch('/upload_profile_picture', { // Create this endpoint in Flask
                method: 'POST',
                body: formData,
                // No 'Content-Type' header needed for FormData; browser sets it
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Profile picture updated successfully!');
                    // Optionally update the image source with the new URL from the server
                    profileAvatarDisplay.src = data.new_profile_pic_url;
                } else {
                    alert('Error updating profile picture: ' + data.message);
                    // Revert to old image if upload fails
                    profileAvatarDisplay.src = "{{ profile_pic_url }}";
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An unexpected error occurred during upload.');
                profileAvatarDisplay.src = "{{ profile_pic_url }}"; // Revert on network error
            });
        }
    });
});