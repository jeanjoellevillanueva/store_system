/**
 * Reloads a component by fetching data from the specified URL and updating the content
 * of the element with the given container ID.
 *
 * @param {string} url - The URL to fetch data from.
 * @param {string} containerId - The ID of the HTML element to update with the fetched data.
 * @param {bool} isLoadingEffect - If you want to add a loading effect in between the fetching.
 * 
 * The response must be HTML.
 * Tip: Use TemplateView in the Django Views.
 */
function reloadComponent(url, containerId, isLoadingEffect=false) {
  if (isLoadingEffect) {
    $(`#${containerId}`).html(
      `<div class="spinner-border" role="status">
        <span class="sr-only">Loading...</span>
      </div>
      `
    );
  }
  axios.get(url)
    .then(function (response) {
      $(`#${containerId}`).html(response.data);
    })
    .catch(function (error) {
      console.error(error);
    });
}


function reloadComponentPost(url, data, header, containerId, isLoadingEffect=false) {
  if (isLoadingEffect) {
    $(`#${containerId}`).html(
      `<div class="spinner-border" role="status">
        <span class="sr-only">Loading...</span>
      </div>
      `
    );
  }
  axios.post(url, data, header)
    .then(function (response) {
      $(`#${containerId}`).html(response.data);
    })
    .catch(function (error) {
      console.error(error);
    });
}

/**
 * Hide/Show the success or error message.
 * @param {string} alertType - Value must be 'Success' or 'Error' ONLY.
 * @param {string} message - The message you wanted to show.
 */
function triggerAlert(alertType, message) {
  $(`#idAlertMessage${alertType}`).html(`${message}.`);
  $(`#idAlert${alertType}`).removeClass('d-none');
  $(`#idAlert${alertType}`).fadeIn();
}
