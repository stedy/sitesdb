$(function()
    {
          $('#dates_table .date').each(function() {
                    var phonecall = Date.parse($(this).text().replace(/(\d{2})\/(\d{2})\/(\d{4})/, '$2/$1/$3'));
                    var now_date = new Date().getTime();
                    if(phonecall >= now_date + 1209600000)
                    {
                    $(this).addClass('call');
                                          }
              }
                  );
    }
 );
