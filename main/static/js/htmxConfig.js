function checkRender(event) {
   if (event.detail.serverResponse.startsWith('<!doctype html>')) {
      console.log('this is a full page render');
   }
   document.removeEventListener('htmx:beforeSwap', checkRender);
   document.addEventListener('htmx:beforeSwap', checkRender);
}

document.addEventListener('htmx:beforeSwap', checkRender);