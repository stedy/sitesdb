$(function () {
         $('#select-send').click(function (event) {

            var selected = this.checked;
          // Iterate each checkbox for sending
         $(':checkbox').each(function () {    this.checked = selected; });
        });
});

