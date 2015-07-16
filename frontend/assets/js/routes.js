define(function() {
  "use strict";

  return function(match) {
    match("", "Home#index");
    match("blog", "Blog#index");
    match("blog/post/:slug/:id", "Post#index");
    match("blog/categoria/:slug/:id", "Blog#category");
    match("blog", "Blog#index");
    match("ajuda/perguntas-frequentes/:slug/:id", "QuestionsGroup#index");
    match("ajuda/perguntas-frequentes", "QuestionsGroups#index");
    match("ajuda/artigo/:slug/:id", "Article#index");
    match("ajuda/secao/:slug/:id", "Help#section");
    match("ajuda", "Help#index");
    match(":slug/:id", "Page#index");
  };
});