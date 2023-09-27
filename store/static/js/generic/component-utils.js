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