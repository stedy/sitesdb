$(function(){
var substringMatcher = function(strs) {
return function findMatches(q, cb) {
var matches, substringRegex;

// an array that will be populated with substring matches
 matches = [];

// regex used to determine if a string contains the substring `q`
    substrRegex = new RegExp(q, 'i');

// iterate through the pool of strings and for any string that
// contains the substring `q`, add it to the `matches` array
$.each(strs, function(i, str) {
      if (substrRegex.test(str)) {
              matches.push(str);
          }
      });

      cb(matches);
          };
      };

var PIs = ['Hill',
'Boeckh',
'Fredricks',
'Menon (as of 3/25/15)',
'Fredricks/Marrazzo',
'Pergam',
'Casper',
'Menon per mod 2/5/15',
'Boech/Englund',
'Green',
'Waghmare',
'Menon',
'Schiffer',
'Casper/Goldman',
'Corey',
'Jerome',
'Menon per mod 5/5/15',
'Brunette',
'Corey/Kong',
'Goldman/Casper',
'Peng',
'Koelle',
'Malhotra',
'Zhu/Corey',
'Hladik',
'Hohl',
'Wald',
'Corey/Wald',
'Corey/Nichols',
'Marr/Corey',
'Marr',
'Nichols',
'Marr/Panackal',
'Marr/Upton',
'Horton',
'Stednick'];

$('#the-basics .typeahead').typeahead({
  hint: true,
  highlight: true,
  minLength: 1
  },
  {
  name: 'PIs',
  source: substringMatcher(PIs)
  });
});
