// function likeGame(button, gameid) {
//     var likeButton = $(button);
//     var neutralButton = $(button).siblings(".neutralButton");
//     var dislikeButton = $(button).siblings(".dislikeButton");
//     likeButton.addClass("active");
//     neutralButton.removeClass("active");
//     dislikeButton.removeClass("active");
  
//     $.post("ajax/likeGame", { gameid: gameid }).done(function(data) {
//       var result = JSON.parse(data);
//       updateLikesValue(likeButton.find(".count"), result.likes);
//       updateLikesValue(neutralButton.find(".count"), result.neutral);
//       updateLikesValue(dislikeButton.find(".count"), result.dislikes);
  
//       if (result.likes < 0) {
//         likeButton.removeClass("active");
//         likeButton.find("img:first").attr("src", "assets/images/icons/like.png");
//       } else {
//         likeButton
//           .find("img:first")
//           .attr("src", "assets/images/icons/like-active.png");
//       }
  
//       dislikeButton
//         .find("img:first")
//         .attr("src", "assets/images/icons/dislike.png");
  
//       neutralButton
//         .find("img:first")
//         .attr("src", "assets/images/icons/neutral.png");
//     });
//   }
  
//   function neutralGame(button, gameid) {
//     var neutralButton = $(button);
//     var dislikeButton = $(button).siblings(".dislikeButton");
//     var likeButton = $(button).siblings(".likeButton");
//     neutralButton.addClass("active");
//     dislikeButton.removeClass("active");
//     likeButton.removeClass("active");
  
//     $.post("ajax/neutralGame", { gameid: gameid }).done(function(data) {
  
//       var result = JSON.parse(data);
//       updateLikesValue(likeButton.find(".count"), result.likes);
//       updateLikesValue(neutralButton.find(".count"), result.neutral);
//       updateLikesValue(dislikeButton.find(".count"), result.dislikes);
  
//       if (result.neutral < 0) {
//         neutralButton.removeClass("active");
//         neutralButton
//           .find("img:first")
//           .attr("src", "assets/images/icons/neutral.png");
//       } else {
//         neutralButton
//           .find("img:first")
//           .attr("src", "assets/images/icons/neutral-active.png");
//       }
  
//       dislikeButton
//         .find("img:first")
//         .attr("src", "assets/images/icons/dislike.png");
  
//       likeButton.find("img:first").attr("src", "assets/images/icons/like.png");
//     });
//   }
  
//   function dislikeGame(button, gameid) {
//     var dislikeButton = $(button);
//     var likeButton = $(button).siblings(".likeButton");
//     var neutralButton = $(button).siblings(".neutralButton");
//     dislikeButton.addClass("active");
//     likeButton.removeClass("active");
//     neutralButton.removeClass("active");
  
//     $.post("ajax/dislikeGame", { gameid: gameid }).done(function(data) {
  
//       var result = JSON.parse(data);
//       updateLikesValue(likeButton.find(".count"), result.likes);
//       updateLikesValue(neutralButton.find(".count"), result.neutral);
//       updateLikesValue(dislikeButton.find(".count"), result.dislikes);
  
//       if (result.dislikes < 0) {
//         dislikeButton.removeClass("active");
//         dislikeButton
//           .find("img:first")
//           .attr("src", "assets/images/icons/dislike.png");
//       } else {
//         dislikeButton
//           .find("img:first")
//           .attr("src", "assets/images/icons/dislike-active.png");
//       }
  
//       likeButton.find("img:first").attr("src", "assets/images/icons/like.png");
  
//       neutralButton
//         .find("img:first")
//         .attr("src", "assets/images/icons/neutral.png");
//     });
//   }
  
//   function updateLikesValue(element, num) {
//     var likesCountVal = element.text() || 0;
//     element.text(parseInt(likesCountVal) + parseInt(num));
//   }
  