function getDetailBeforeSwap(event) {
   console.group('Swap details');
   if (event.detail.target === document.body) {
      console.log('Full page swap');
   } else {
      console.log(`Partial swap`);
   }
   console.group('Before swap');
   console.log(event.detail);
   console.groupEnd();
}

function getDetailAfterSwap(event) {
   console.group('After swap');
   console.log(event.detail);
   console.groupEnd();
   console.groupEnd();
}

document.body.addEventListener('htmx:beforeSwap', getDetailBeforeSwap);
document.body.addEventListener('htmx:afterSettle', getDetailAfterSwap);
