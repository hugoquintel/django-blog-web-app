document.addEventListener('alpine:init', () => {
   Alpine.store('utils', {
      displayImage(ele) {
         [file] = ele.files;
         let fileName = '';
         let src = '';
         if (file) {
            src = URL.createObjectURL(file);
            fileName = file.name;
            Alpine.nextTick(() => {
               URL.revokeObjectURL(src);
            });
         }
         return [src, fileName];
      },

      createBlogSectionForm(emptyFormEle, totalForm) {
         const emptyForm = emptyFormEle.cloneNode(true);
         emptyForm.innerHTML = emptyForm.innerHTML.replaceAll('__prefix__', totalForm);
         return emptyForm.firstElementChild;
      },
   });
});
