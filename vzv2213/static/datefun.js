$(function()
    {
          $('#dates_table .date').each(function() {
                    var phonecall = Date.parse($(this).text().replace(/(\d{2})\/(\d{2})\/(\d{2})/, '$1/$2/$3'));
                    var now_date = new Date().getTime();
                    if(phonecall <= now_date + 1210000000 && phonecall > now_date)
                    {
                    $(this).addClass('call');
                                          }
                    if(phonecall > now_date - 1210000000 && phonecall < now_date)
                    {
                      $(this).addClass('past');
                    }
              }
                  );
    }
 );
