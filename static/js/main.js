// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
  // ----- Task Search Filter -----
  var searchInput = document.getElementById('taskSearch');
  if (searchInput) {
    searchInput.addEventListener('keyup', function() {
      var filter = searchInput.value.toUpperCase();
      var table = document.getElementById('tasksTable');
      var tr = table.getElementsByTagName('tr');
      for (var i = 0; i < tr.length; i++) {
        var td = tr[i].getElementsByTagName('td')[0];
        if (td) {
          var txtValue = td.textContent || td.innerText;
          tr[i].style.display = (txtValue.toUpperCase().indexOf(filter) > -1) ? "" : "none";
        }
      }
    });
  }

    // ----- Toggle Completed Tasks -----
    var toggleCompletedButton = document.getElementById('toggleCompleted');
    if (toggleCompletedButton) {
      toggleCompletedButton.addEventListener('click', function() {
        var table = document.getElementById('tasksTable');
        var tr = table.getElementsByTagName('tr');
        for (var i = 0; i < tr.length; i++) {
          // Assuming the "Completed" column is the fourth column (index 3)
          var tdCompleted = tr[i].getElementsByTagName('td')[3];
          if (tdCompleted) {
            // Look for the <select> element within the cell
            var selectElement = tdCompleted.querySelector('select');
            if (selectElement && selectElement.value.trim() === 'Yes') {
              // Toggle the row display
              tr[i].style.display = (tr[i].style.display === "none") ? "" : "none";
            }
          }
        }
      });
    }


  // ----- Update Completed Status via Dropdown -----
  // Attach change event listener to all dropdowns with class 'completed-dropdown'
  var dropdowns = document.getElementsByClassName('completed-dropdown');
  Array.from(dropdowns).forEach(function(dropdown) {
    dropdown.addEventListener('change', function() {
      var taskId = this.getAttribute('data-task-id');
      var newValue = this.value; // "Yes" or "No"

      // Send AJAX (fetch) request to update the completed status
      fetch('/tasks/' + taskId + '/update_completed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({completed: newValue})
      })
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        if (data.status === 'success') {
          // Optionally, you can update the UI further if needed
          console.log('Task updated successfully.');
        } else {
          console.error('Error updating task:', data.message);
        }
      })
      .catch(function(error) {
        console.error('Fetch error:', error);
      });
    });
  });
});
