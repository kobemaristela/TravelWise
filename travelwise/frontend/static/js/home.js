$(function () {
  "use strict";

  $(".js-menu-toggle").click(function (e) {
    var $this = $(this);

    if ($("body").hasClass("show-sidebar")) {
      $("body").removeClass("show-sidebar");
      $this.removeClass("active");
    } else {
      $("body").addClass("show-sidebar");
      $this.addClass("active");
    }

    e.preventDefault();
  });

  // close by clicking outside
  $(document).mouseup(function (e) {
    var container = $(".sidebar");
    if (!container.is(e.target) && container.has(e.target).length === 0) {
      if ($("body").hasClass("show-sidebar")) {
        $("body").removeClass("show-sidebar");
        $("body").find(".js-menu-toggle").removeClass("active");
      }
    }
  });

  document.getElementById('new-plan-button').addEventListener('click', function(e) {
    api.createPlan()
    .then(function(response) {
        const planId = response.planId;
        
        window.location.href = `/create/?id=${planId}`;
    })
    .catch(function (error) {
        alert('Failed to create plan');
    });
  });
});

