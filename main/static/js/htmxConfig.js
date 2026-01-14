// document.addEventListener('htmx:beforeSwap', function (event) {
//    // Optimize this
//    if (event.detail.serverResponse.startsWith('<!doctype html>')) {
//       // Remember to remove this
//       console.log('this is a full page re-rendered');
//       event.detail.target = document.querySelector('body');
//    }
// });

function checkRender(event) {
   if (event.detail.serverResponse.startsWith('<!doctype html>')) {
      // Remember to remove this
      console.log('this is a full page render');
      // event.detail.target = document.querySelector('body');
   }
   document.removeEventListener('htmx:beforeSwap', checkRender);
   document.addEventListener('htmx:beforeSwap', checkRender);
}

document.addEventListener('htmx:beforeSwap', checkRender);