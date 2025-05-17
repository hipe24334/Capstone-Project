
    $('#imagetag').click(function(){
      $('#upload').click();
    });

    $('#change').click(function(){
      $('#upload').click();
    });

    $('#attachement').click(function(){
      $('#upload-file').click();
      $(".fileDisplay").css("display", "block"); 
  });

    

    $(function(){
      $('#upload').change(function(){
        alert(1);
        var input = this;
        var url = $(this).val();
        var ext = url.substring(url.lastIndexOf('.') + 1).toLowerCase();
        if (input.files && input.files[0]&& (ext == "gif" || ext == "png" || ext == "jpeg" || ext == "jpg")) 
        {
            var reader = new FileReader();

            reader.onload = function (e) {
              $('#imagetag').attr('src', e.target.result);
            }
          reader.readAsDataURL(input.files[0]);
        }
        else
        {
          $('#imagetag').attr('src', '/static/images/150x151.png');
        }
      });

    });

    $(function(){
      $('#upload-file').change(function(){
        var input = this;
        var url = $(this).val();
        var ext = url.substring(url.lastIndexOf('.') + 1).toLowerCase();
        if (input.files && input.files[0]&& (ext == "gif" || ext == "png" || ext == "jpeg" || ext == "jpg")) 
        {
            var reader = new FileReader();

            reader.onload = function (e) {
              $('#imageDisplay').attr('src', e.target.result);
            }
          reader.readAsDataURL(input.files[0]);
        }
        else
        {
          $('#imageDisplay').attr('src', '/static/images/150x151.png');
        }
        do {
          secretkeyN = prompt("Nhập khoá bí mật N (PrivateKey có định dạng (N,d)): ");
        } while (!/^\d+$/.test(secretkeyN));
        do {
          secretkeyE = prompt("Nhập khoá bí mật d (PrivateKey có định dạng (N,d)): ");
        } while (!/^\d+$/.test(secretkeyE));
         
        $('#secret_key_sender_E').val(secretkeyE);
        $('#secret_key_sender_N').val(secretkeyN);
      });
    });
