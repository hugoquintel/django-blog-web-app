function showHidePasswords() {
   const passwordEles = document.querySelectorAll('input[type="password"]');
   const checkbox = document.querySelector('input[type="checkbox"]');
   function changeInputType(inputs, type) {
      inputs.forEach((input) => {
         input.type = type;
      });
   }
   checkbox.onchange = (event) => {
      if (event.target.checked) {
         changeInputType(passwordEles, 'text');
      } else {
         changeInputType(passwordEles, 'password');
      }
   };
}

showHidePasswords();
document.addEventListener('htmx:afterSwap', function (event) {
   console.log("hello")
   showHidePasswords();
});
