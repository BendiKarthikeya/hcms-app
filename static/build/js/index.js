/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./static/index/index.js":
/*!*******************************!*\
  !*** ./static/index/index.js ***!
  \*******************************/
/***/ (() => {

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }
function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }
function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && iter[Symbol.iterator] != null || iter["@@iterator"] != null) return Array.from(iter); }
function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }
function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i]; return arr2; }
var confirmModal = {
  ar: "تأكيد",
  de: "Bestätigen",
  es: "Confirmar",
  en: "Confirm",
  fr: "Confirmer"
};
var cancelModal = {
  ar: "إلغاء",
  de: "Abbrechen",
  es: "Cancelar",
  en: "Cancel",
  fr: "Annuler"
};
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
function handleSidebarToggle() {
  // Delay the execution slightly to allow existing toggle logic to finish
  setTimeout(function () {
    var isOpen = !$('.oh-wrapper-main').hasClass('oh-wrapper-main--closed');
    localStorage.setItem('sidebarOpen', isOpen);
  }, 50);
}
function addToSelectedId(newIds, storeKey) {
  ids = JSON.parse($("#".concat(storeKey)).attr("data-ids") || "[]");
  ids = [].concat(_toConsumableArray(ids), _toConsumableArray(newIds.map(String)));
  ids = Array.from(new Set(ids));
  $("#".concat(storeKey)).attr("data-ids", JSON.stringify(ids));
}
function togglePublicComments() {
  if ($('#id_disable_comments').is(':checked')) {
    $('#id_public_comments').prop('checked', false);
    $('#id_public_comments_parent_div').hide();
  } else {
    $('#id_public_comments_parent_div').show();
  }
}
function attendanceDateChange(selectElement) {
  var selectedDate = selectElement.val();
  var parentForm = selectElement.parents().closest("form");
  var shiftId = parentForm.find("[name=shift_id]").val();
  $.ajax({
    type: "post",
    url: "/attendance/update-date-details",
    data: {
      csrfmiddlewaretoken: getCookie("csrftoken"),
      attendance_date: selectedDate,
      shift_id: shiftId
    },
    success: function success(response) {
      parentForm.find("[name=minimum_hour]").val(response.minimum_hour);
    }
  });
}
function getAssignedLeave(employeeElement) {
  var employeeId = employeeElement.val();
  $.ajax({
    type: "get",
    url: "/payroll/get-assigned-leaves",
    data: {
      employeeId: employeeId
    },
    dataType: "json",
    success: function success(response) {
      var rows = "";
      for (var index = 0; index < response.length; index++) {
        var element = response[index];
        rows = rows + "<tr class=\"toggle-highlight\"><td>".concat(element.leave_type_id__name, "</td><td>").concat(element.available_days, "</td><td>").concat(element.carryforward_days, "</td></tr>");
      }
      $("#availableTableBody").html($(rows));
      var newLeaves = "";
      for (var _index = 0; _index < response.length; _index++) {
        var leave = response[_index];
        newLeaves = newLeaves + "<option value=\"".concat(leave.leave_type_id__id, "\">").concat(leave.leave_type_id__name, "</option>");
      }
      $("#id_leave_type_id").html(newLeaves);
      removeHighlight();
    }
  });
}
function selectSelected(viewId) {
  var storeKey = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "selectedInstances";
  ids = JSON.parse($("#".concat(storeKey)).attr("data-ids") || "[]");
  $.each(ids, function (indexInArray, valueOfElement) {
    $("".concat(viewId, " .oh-sticky-table__tbody .list-table-row[value=").concat(valueOfElement, "]")).prop("checked", true).change();
    $("".concat(viewId, " tbody .list-table-row[value=").concat(valueOfElement, "]")).prop("checked", true).change();
  });
  $("".concat(viewId, " .oh-sticky-table__tbody .list-table-row,").concat(viewId, " tbody .list-table-row")).change(function (e) {
    id = $(this).val();
    ids = JSON.parse($("#".concat(storeKey)).attr("data-ids") || "[]");
    ids = Array.from(new Set(ids));
    var index = ids.indexOf(id);
    if (!ids.includes(id)) {
      ids.push(id);
    } else {
      if (!$(this).is(":checked")) {
        ids.splice(index, 1);
      }
    }
    $("#".concat(storeKey)).attr("data-ids", JSON.stringify(ids));
  });
  if (viewId) {
    reloadSelectedCount($("#count_".concat(viewId)), storeKey);
  }
}

// Switch General Tab
function switchGeneralTab(e) {
  // DO NOT USE GENERAL TABS TWICE ON A SINGLE PAGE.
  e.preventDefault();
  e.stopPropagation();
  var clickedEl = e.target.closest(".oh-general__tab-link");
  var targetSelector = clickedEl.dataset.target;

  // Remove active class from all the tabs
  $(".oh-general__tab-link").removeClass("oh-general__tab-link--active");
  // Remove active class to the clicked tab
  clickedEl.classList.add("oh-general__tab-link--active");

  // Hide all the general tabs
  $(".oh-general__tab-target").addClass("d-none");
  // Show the tab with the chosen target
  $(".oh-general__tab-target".concat(targetSelector)).removeClass("d-none");
}
function toggleReimbursmentType(element) {
  if (element.val() == "reimbursement") {
    $("#objectCreateModalTarget [name=attachment]").parent().show();
    $("#objectCreateModalTarget [name=attachment]").attr("required", true);
    $("#objectCreateModalTarget [name=leave_type_id]").parent().hide().attr("required", false);
    $("#objectCreateModalTarget [name=cfd_to_encash]").parent().hide().attr("required", false);
    $("#objectCreateModalTarget [name=ad_to_encash]").parent().hide().attr("required", false);
    $("#objectCreateModalTarget [name=amount]").parent().show().attr("required", true);
    $("#objectCreateModalTarget #availableTable").hide().attr("required", false);
    $("#objectCreateModalTarget [name=bonus_to_encash]").parent().hide().attr("required", false);
  } else if (element.val() == "leave_encashment") {
    $("#objectCreateModalTarget [name=attachment]").parent().hide();
    $("#objectCreateModalTarget [name=attachment]").attr("required", false);
    $("#objectCreateModalTarget [name=leave_type_id]").parent().show().attr("required", true);
    $("#objectCreateModalTarget [name=cfd_to_encash]").parent().show().attr("required", true);
    $("#objectCreateModalTarget [name=ad_to_encash]").parent().show().attr("required", true);
    $("#objectCreateModalTarget [name=amount]").parent().hide().attr("required", false);
    $("#objectCreateModalTarget #availableTable").show().attr("required", true);
    $("#objectCreateModalTarget [name=bonus_to_encash]").parent().hide().attr("required", false);
    // #819
    $("#objectCreateModalTarget [name=employee_id]").trigger("change");
  } else if (element.val() == "bonus_encashment") {
    $("#objectCreateModalTarget [name=attachment]").parent().hide();
    $("#objectCreateModalTarget [name=attachment]").attr("required", false);
    $("#objectCreateModalTarget [name=leave_type_id]").parent().hide().attr("required", false);
    $("#objectCreateModalTarget [name=cfd_to_encash]").parent().hide().attr("required", false);
    $("#objectCreateModalTarget [name=ad_to_encash]").parent().hide().attr("required", false);
    $("#objectCreateModalTarget [name=amount]").parent().hide().attr("required", false);
    $("#objectCreateModalTarget #availableTable").hide().attr("required", false);
    $("#objectCreateModalTarget [name=bonus_to_encash]").parent().show().attr("required", true);
  }
}
function reloadSelectedCount(targetElement) {
  var storeKey = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "selectedInstances";
  var count = JSON.parse($("#".concat(storeKey)).attr("data-ids") || "[]").length;
  id = targetElement.attr("id");
  if (id) {
    id = id.split("count_")[1];
  }
  if (count) {
    targetElement.html(count);
    targetElement.parent().removeClass("d-none");
    $("#unselect_".concat(id, ", #export_").concat(id, ", #bulk_udate_").concat(id)).removeClass("d-none");
  } else {
    targetElement.parent().addClass("d-none");
    $("#unselect_".concat(id, ", #export_").concat(id, ", #bulk_udate_").concat(id)).addClass("d-none");
  }
}
function removeHighlight() {
  setTimeout(function () {
    $(".toggle-highlight").removeClass("toggle-highlight");
  }, 200);
}
function removeId(element) {
  var storeKey = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "selectedInstances";
  id = element.val();
  viewId = element.attr("data-view-id");
  ids = JSON.parse($("#".concat(storeKey)).attr("data-ids") || "[]");
  var elementToRemove = 5;
  if (ids[ids.length - 1] === id) {
    ids.pop();
  }
  ids = JSON.stringify(ids);
  $("#".concat(storeKey)).attr("data-ids", ids);
}
function bulkStageUpdate(canIds, stageId, preStageId) {
  $.ajax({
    type: "POST",
    url: "/recruitment/candidate-stage-change?bulk=True",
    data: {
      csrfmiddlewaretoken: getCookie("csrftoken"),
      canIds: JSON.stringify(canIds),
      stageId: stageId
    },
    success: function success(response, textStatus, jqXHR) {
      if (jqXHR.status === 200) {
        $("#stageLoad" + preStageId).click();
        $("#stageLoad" + stageId).click();
      }
      if (response.message) {
        Swal.fire({
          title: response.message,
          text: "Total vacancy is ".concat(response.vacancy, "."),
          // Using template literals
          icon: "info",
          confirmButtonText: "Ok"
        });
      }
    }
  });
}
function updateCandStage(canIds, stageId, preStageId) {
  $.ajax({
    type: "POST",
    url: "/recruitment/candidate-stage-change?bulk=false",
    data: {
      csrfmiddlewaretoken: getCookie("csrftoken"),
      canIds: canIds,
      stageId: stageId
    },
    success: function success(response, textStatus, jqXHR) {
      if (jqXHR.status === 200) {
        $("#stageLoad" + preStageId).click();
        $("#stageLoad" + stageId).click();
      }
      if (response.message) {
        Swal.fire({
          title: response.message,
          text: "Total vacancy is ".concat(response.vacancy, "."),
          // Using template literals
          icon: "info",
          confirmButtonText: "Ok"
        });
      }
    }
  });
}
function checkSequence(element) {
  var preStageId = $(element).data("stage_id");
  var canIds = $(element).data("cand_id");
  var stageOrderJson = $(element).attr("data-stage_order");
  var stageId = $(element).val();
  var parsedStageOrder = JSON.parse(stageOrderJson);
  var stage = parsedStageOrder.find(function (stage) {
    return stage.id == stageId;
  });
  var preStage = parsedStageOrder.find(function (stage) {
    return stage.id == preStageId;
  });
  var stageOrder = parsedStageOrder.map(function (stage) {
    return stage.id;
  });
  if (stageOrder.indexOf(parseInt(stageId)) != stageOrder.indexOf(parseInt(preStageId)) + 1 && stage.type != "cancelled") {
    Swal.fire({
      title: "Confirm",
      text: "Are you sure to change the candidate from ".concat(preStage.stage, " stage to ").concat(stage.stage, " stage"),
      icon: "info",
      showCancelButton: true,
      confirmButtonColor: "#008000",
      cancelButtonColor: "#d33",
      confirmButtonText: "Confirm"
    }).then(function (result) {
      if (result.isConfirmed) {
        updateCandStage(canIds, stageId, preStageId);
      }
    });
  } else {
    updateCandStage(canIds, stageId, preStageId);
  }
}
function reloadMessage(e) {
  $("#reloadMessagesButton").click();
}
function htmxLoadIndicator(e) {
  var target = $(e).attr("hx-target");
  var table = $(target).find("table");
  var card = $(target).find(".oh-card__body");
  var kanban = $(target).find(".oh-kanban-card");
  if (table.length) {
    table.addClass("is-loading");
    table.find("th, td").empty();
  }
  if (card.length) {
    card.addClass("is-loading");
  }
  if (kanban.length) {
    kanban.addClass("is-loading");
  }
  if (!table.length && !card.length && !kanban.length) {
    $(target).html("<div class=\"animated-background\"></div>");
  }
}
function ajaxWithResponseHandler(event) {
  $(event.target).each(function () {
    $.each(this.attributes, function () {
      if (this.specified && this.name === "hx-on-htmx-after-request") {
        eval(this.value);
      }
    });
  });
}
function handleHtmxTarget(event, path, verb) {
  var targetElement;
  var hxTarget = $(event.target).attr("hx-target");
  if (hxTarget) {
    if (hxTarget === "this") {
      targetElement = $(event.target);
    } else if (hxTarget.startsWith("closest ")) {
      var selector = hxTarget.replace("closest ", "").trim();
      targetElement = $(event.target).closest(selector);
    } else if (hxTarget.startsWith("find ")) {
      var selector = hxTarget.replace("find ", "").trim();
      targetElement = $(event.target).find(selector).first();
    } else if (hxTarget === "next") {
      targetElement = $(event.target).next();
    } else if (hxTarget.startsWith("next ")) {
      var selector = hxTarget.replace("next ", "").trim();
      targetElement = $(event.target).nextAll(selector).first();
    } else if (hxTarget === "previous") {
      targetElement = $(event.target).prev();
    } else if (hxTarget.startsWith("previous ")) {
      var selector = hxTarget.replace("previous ", "").trim();
      targetElement = $(event.target).prevAll(selector).first();
    } else {
      targetElement = $(hxTarget);
    }
    hxTarget = targetElement.length ? targetElement[0] : null;
  } else if (path && verb) {
    hxTarget = event.target;
  }
  return hxTarget;
}
function hxConfirm(element, messageText) {
  Swal.fire({
    html: messageText,
    icon: "question",
    showCancelButton: true,
    confirmButtonColor: "#008000",
    cancelButtonColor: "#d33",
    confirmButtonText: "Confirm",
    cancelButtonText: "Cancel",
    reverseButtons: true
  }).then(function (result) {
    if (result.isConfirmed) {
      htmx.trigger(element, 'confirmed');
    } else {
      element.checked = false;
      return false;
    }
  });
}
function handleDownloadAndRefresh(event, url) {
  // Use in import_popup.html file
  event.preventDefault();

  // Create a temporary hidden iframe to trigger the download
  var iframe = document.createElement("iframe");
  iframe.style.display = "none";
  iframe.src = url;
  document.body.appendChild(iframe);

  // Refresh the page after a short delay
  setTimeout(function () {
    document.body.removeChild(iframe); // Clean up the iframe
    window.location.reload(); // Refresh the page
  }, 500); // Adjust the delay as needed
}

function toggleCommentButton(e) {
  var $button = $(e).closest("form").find("#commentButton");
  $button.toggle($(e).val().trim() !== "");
}
function updateUserPanelCount(e) {
  var count = $(e).closest(".oh-sticky-table__tr").find(".oh-user-panel").length;
  setTimeout(function () {
    var $permissionCountSpan = $(e).closest(".oh-permission-table--toggle").parent().find(".oh-permission-count");
    var currentText = $permissionCountSpan.text();
    var firstSpaceIndex = currentText.indexOf(" ");
    var textAfterNumber = currentText.slice(firstSpaceIndex + 1);
    var newText = count + " " + textAfterNumber;
    $permissionCountSpan.text(newText);
  }, 100);
}
function enlargeImage(src, $element) {
  $(".enlargeImageContainer").empty();
  var enlargeImageContainer = $element.parents().closest("li").find(".enlargeImageContainer");
  enlargeImageContainer.empty();
  style = "width:100%; height:90%; box-shadow: 0 10px 10px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.2); background:white";
  var enlargedImage = $("<iframe>").attr({
    src: src,
    style: style
  });
  var name = $("<span>").text(src.split("/").pop().replace(/_/g, " "));
  enlargeImageContainer.append(enlargedImage);
  enlargeImageContainer.append(name);
  setTimeout(function () {
    enlargeImageContainer.show();
    var iframe = document.querySelector("iframe").contentWindow;
    var iframe_document = iframe.document;
    iframe_image = iframe_document.getElementsByTagName("img")[0];
    $(iframe_image).attr("style", "width:100%; height:100%;");
  }, 100);
}
function hideEnlargeImage() {
  var enlargeImageContainer = $(".enlargeImageContainer");
  enlargeImageContainer.empty();
}
function submitForm(elem) {
  $(elem).siblings(".add_more_submit").click();
}
function show_answer(element) {
  var $parentItem = $(element).closest(".oh-faq__item");
  var isShown = $parentItem.hasClass("oh-faq__item--show");
  $(".oh-faq__item--show").removeClass("oh-faq__item--show");
  if (!isShown) {
    $parentItem.addClass("oh-faq__item--show");
  }
}
var originalConfirm = window.confirm;
// Override the default confirm function with SweetAlert
window.confirm = function (message) {
  var event = window.event || {};
  event.preventDefault();
  var languageCode = $("#main-section-data").attr("data-lang") || "en";
  var confirm = confirmModal[languageCode];
  var cancel = cancelModal[languageCode];
  $("#confirmModalBody").html(message);
  var submit = false;
  Swal.fire({
    text: message,
    icon: "question",
    showCancelButton: true,
    confirmButtonColor: "#008000",
    cancelButtonColor: "#d33",
    confirmButtonText: confirm,
    cancelButtonText: cancel
  }).then(function (result) {
    if (result.isConfirmed) {
      var _event$target$htmxIn, _event$target$htmxIn2;
      var path = (_event$target$htmxIn = event.target["htmx-internal-data"]) === null || _event$target$htmxIn === void 0 ? void 0 : _event$target$htmxIn.path;
      var verb = (_event$target$htmxIn2 = event.target["htmx-internal-data"]) === null || _event$target$htmxIn2 === void 0 ? void 0 : _event$target$htmxIn2.verb;
      var hxTarget = handleHtmxTarget(event, path, verb);
      var hxVals = $(event.target).attr("hx-vals") ? JSON.parse($(event.target).attr("hx-vals")) : {};
      var hxSwap = $(event.target).attr("hx-swap");
      $(event.target).each(function () {
        $.each(this.attributes, function () {
          if (this.specified && this.name === "hx-on-htmx-before-request") {
            eval(this.value);
          }
        });
      });
      if (event.target.tagName.toLowerCase() === "form") {
        if (path && verb) {
          // Collect all form values
          var formData = new FormData(event.target);
          var values = {};
          formData.forEach(function (value, key) {
            values[key] = value;
          });

          // Merge with hx-vals, if any
          Object.assign(values, hxVals);
          htmx.ajax(verb.toUpperCase(), path, {
            target: hxTarget,
            swap: hxSwap,
            values: values
          }).then(function (response) {
            ajaxWithResponseHandler(event);
          });
        } else {
          event.target.submit(); // fallback
        }
      } else if (event.target.tagName.toLowerCase() === "a") {
        if (event.target.href) {
          window.location.href = event.target.href;
        } else {
          if (verb === "post") {
            htmx.ajax("POST", path, {
              target: hxTarget,
              swap: hxSwap,
              values: hxVals
            }).then(function (response) {
              ajaxWithResponseHandler(event);
            });
          } else {
            htmx.ajax("GET", path, {
              target: hxTarget,
              swap: hxSwap,
              values: hxVals
            }).then(function (response) {
              ajaxWithResponseHandler(event);
            });
          }
        }
      } else {
        if (verb === "post") {
          htmx.ajax("POST", path, {
            target: hxTarget,
            swap: hxSwap,
            values: hxVals
          }).then(function (response) {
            ajaxWithResponseHandler(event);
          });
        } else {
          htmx.ajax("GET", path, {
            target: hxTarget,
            swap: hxSwap,
            values: hxVals
          }).then(function (response) {
            ajaxWithResponseHandler(event);
          });
        }
      }
    }
  });
};
var excludeIds = "#employeeSearch";
// To exclude more elements, add their IDs (prefixed with '#') or class names (prefixed with '.'), separated by commas to 'excludeIds'.
setTimeout(function () {
  $("[name='search']").not(excludeIds).focus();
}, 100);
$("#close").attr("class", "oh-activity-sidebar__header-icon me-2 oh-activity-sidebar__close md hydrated");
$("body").on("click", ".select2-search__field", function (e) {
  //When click on Select2 fields in filter form,Auto close issue
  e.stopPropagation();
});
var nav = $("section.oh-wrapper.oh-main__topbar");
nav.after($("\n  <div id=\"filterTagContainerSectionNav\" class=\"oh-titlebar-container__filters mb-2 mt-0 oh-wrapper\"></div>\n  "));
$(function () {
  var $wrapper = $('.oh-wrapper-main');
  var sidebarOpen = localStorage.getItem('sidebarOpen');
  if (sidebarOpen === 'false') {
    $wrapper.addClass('oh-wrapper-main--closed');
  } else {
    $wrapper.removeClass('oh-wrapper-main--closed');
  }
  $('#sidebar').on('mouseleave', function () {
    if (localStorage.getItem('sidebarOpen') === 'false') {
      $wrapper.addClass('oh-wrapper-main--closed');
    }
  });
});
$(document).on('click', '.oh-kanban__card-body-collapse', function (e) {
  e.preventDefault();
  var $cardBody = $(this).closest('.oh-kanban__card-body');
  $cardBody.find('.oh-kanban__card-content').toggleClass('oh-kanban__card-content--hide');
  $(this).toggleClass('oh-kanban__card-collapse--down');
});
$(document).on("htmx:beforeRequest", function (event, data) {
  if (!Array.from(event.target.getAttributeNames()).some(function (attr) {
    return attr.startsWith("hx-on");
  })) {
    var response = event.detail.xhr.response;
    var target = $(event.detail.elt.getAttribute("hx-target"));
    var avoid_target_ids = ["BiometricDeviceTestFormTarget", "reloadMessages", "infinite", "OtpContainer"];
    var avoid_target_class = ["oh-badge--small"];
    if (!target.closest("form").length && !avoid_target_ids.includes(target.attr("id")) && !avoid_target_class.some(function (cls) {
      return target.hasClass(cls);
    })) {
      target.html("<div class=\"animated-background\"></div>");
    }
  }
});
$(document).on("click", ".select2-selection__choice__remove", function (event) {
  if ($('[role="tooltip"]:visible').length) {
    $('[role="tooltip"]').hide();
  }
});
$(document).on("keydown", function (event) {
  // Check if the cursor is not focused on an input field
  var isInputFocused = $(document.activeElement).is("input, textarea, select");
  if (event.keyCode === 27) {
    // Key code 27 for Esc in keypad
    $(".oh-modal--show").removeClass("oh-modal--show");
    $(".oh-activity-sidebar--show").removeClass("oh-activity-sidebar--show");
  }
  if (event.keyCode === 46) {
    // Key code 46 for delete in keypad
    // If there have any objectDetailsModal with oh-modal--show
    // take delete button inside that else take the delete button from navbar Actions
    if (!isInputFocused) {
      var $modal = $(".oh-modal--show");
      var $deleteButton = $modal.length ? $modal.find('[data-action="delete"]') : $(".oh-dropdown").find('[data-action="delete"]');
      if ($deleteButton.length) {
        $deleteButton.click();
        $deleteButton[0].click();
      }
    }
  } else if (event.keyCode === 107) {
    // Key code for the + key on the numeric keypad
    if (!isInputFocused) {
      // Click the create option from navbar of current page
      $('[data-action="create"]').click();
    }
  } else if (event.keyCode === 39) {
    // Key code for the right arrow key
    if (!isInputFocused) {
      var $modal = $(".oh-modal--show");
      var $nextButton = $modal.length ? $modal.find('[data-action="next"]') : $('[data-action="next"]'); // Click on the next button in detail view modal
      if ($nextButton.length) {
        $nextButton[0].click();
      }
    }
  } else if (event.keyCode === 37) {
    // Key code for the left arrow key
    if (!isInputFocused) {
      // Click on the previous button in detail view modal
      var $modal = $(".oh-modal--show");
      var $previousButton = $modal.length ? $modal.find('[data-action="previous"]') : $('[data-action="previous"]');
      if ($previousButton.length) {
        $previousButton[0].click();
      }
    }
  }
});
$(document).on("click", function (event) {
  if (!$(event.target).closest("#enlargeImageContainer").length) {
    hideEnlargeImage();
  }
});
$(document).on("htmx:afterSwap", function () {
  if ($("[data-summernote]").length > 0) {
    $("[data-summernote]").summernote({
      height: 300,
      codeviewFilter: false,
      codeviewIframeFilter: false,
      callbacks: {
        onChange: function onChange(contents) {
          $('[name="body"]').val(contents);
        }
      }
    });
  }
});

/***/ }),

/***/ "./static/src/scss/main.scss":
/*!***********************************!*\
  !*** ./static/src/scss/main.scss ***!
  \***********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
// extracted by mini-css-extract-plugin


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/chunk loaded */
/******/ 	(() => {
/******/ 		var deferred = [];
/******/ 		__webpack_require__.O = (result, chunkIds, fn, priority) => {
/******/ 			if(chunkIds) {
/******/ 				priority = priority || 0;
/******/ 				for(var i = deferred.length; i > 0 && deferred[i - 1][2] > priority; i--) deferred[i] = deferred[i - 1];
/******/ 				deferred[i] = [chunkIds, fn, priority];
/******/ 				return;
/******/ 			}
/******/ 			var notFulfilled = Infinity;
/******/ 			for (var i = 0; i < deferred.length; i++) {
/******/ 				var [chunkIds, fn, priority] = deferred[i];
/******/ 				var fulfilled = true;
/******/ 				for (var j = 0; j < chunkIds.length; j++) {
/******/ 					if ((priority & 1 === 0 || notFulfilled >= priority) && Object.keys(__webpack_require__.O).every((key) => (__webpack_require__.O[key](chunkIds[j])))) {
/******/ 						chunkIds.splice(j--, 1);
/******/ 					} else {
/******/ 						fulfilled = false;
/******/ 						if(priority < notFulfilled) notFulfilled = priority;
/******/ 					}
/******/ 				}
/******/ 				if(fulfilled) {
/******/ 					deferred.splice(i--, 1)
/******/ 					var r = fn();
/******/ 					if (r !== undefined) result = r;
/******/ 				}
/******/ 			}
/******/ 			return result;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/jsonp chunk loading */
/******/ 	(() => {
/******/ 		// no baseURI
/******/ 		
/******/ 		// object to store loaded and loading chunks
/******/ 		// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 		// [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
/******/ 		var installedChunks = {
/******/ 			"/js/index": 0,
/******/ 			"css/main": 0
/******/ 		};
/******/ 		
/******/ 		// no chunk on demand loading
/******/ 		
/******/ 		// no prefetching
/******/ 		
/******/ 		// no preloaded
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 		
/******/ 		__webpack_require__.O.j = (chunkId) => (installedChunks[chunkId] === 0);
/******/ 		
/******/ 		// install a JSONP callback for chunk loading
/******/ 		var webpackJsonpCallback = (parentChunkLoadingFunction, data) => {
/******/ 			var [chunkIds, moreModules, runtime] = data;
/******/ 			// add "moreModules" to the modules object,
/******/ 			// then flag all "chunkIds" as loaded and fire callback
/******/ 			var moduleId, chunkId, i = 0;
/******/ 			if(chunkIds.some((id) => (installedChunks[id] !== 0))) {
/******/ 				for(moduleId in moreModules) {
/******/ 					if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 						__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 					}
/******/ 				}
/******/ 				if(runtime) var result = runtime(__webpack_require__);
/******/ 			}
/******/ 			if(parentChunkLoadingFunction) parentChunkLoadingFunction(data);
/******/ 			for(;i < chunkIds.length; i++) {
/******/ 				chunkId = chunkIds[i];
/******/ 				if(__webpack_require__.o(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 					installedChunks[chunkId][0]();
/******/ 				}
/******/ 				installedChunks[chunkId] = 0;
/******/ 			}
/******/ 			return __webpack_require__.O(result);
/******/ 		}
/******/ 		
/******/ 		var chunkLoadingGlobal = self["webpackChunkopenhrms_core"] = self["webpackChunkopenhrms_core"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module depends on other loaded chunks and execution need to be delayed
/******/ 	__webpack_require__.O(undefined, ["css/main"], () => (__webpack_require__("./static/index/index.js")))
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["css/main"], () => (__webpack_require__("./static/src/scss/main.scss")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;