define(function() {
  "use strict";

  return function(match) {
    match('', 'Home#index');
    match('sobre', 'About#index');
    match('test', 'Test#index');
  };
});