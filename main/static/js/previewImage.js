id_picture.onchange = () => {
   const [file] = id_picture.files;
   if (file) {
      profile_picture.src = URL.createObjectURL(file);
      upload_btn.innerHTML = `<i class="fa-solid fa-upload"></i> ${file.name}`;
      profile_picture.onload = () => {
         URL.revokeObjectURL(profile_picture.src);
      };
   }
};
