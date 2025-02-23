document.addEventListener('DOMContentLoaded', (event) => {
    function index_for_list_items() {
        // console.log(document.querySelectorAll('#task-list li'));
        document.querySelectorAll('#task-list li').forEach((item, index) => {
            // console.log('Indexing for list item:', item);
            item.style.setProperty('--index', index + 1);
        });
        console.log('Indexing for list items done');
    }

    index_for_list_items();
});