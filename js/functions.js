var bar_on_screen = !1,
	search_mode = !1,
	scrollable = !0,
	found_list = [],
	curpos = 0,
	curpos_s = 0,
	lastScrollTop = 0;

function addFunctionalities(e) {
	$("#" + ids[e].toString()).on("webkitfullscreenchange mozfullscreenchange fullscreenchange", function (e) {
		"FullscreenOff" == (document.fullScreen || document.mozFullScreen || document.webkitIsFullScreen ? "FullscreenOn" : "FullscreenOff") && this.player.pause()
	});
	$("#"+ids[e].toString()).get(0).player.on("contextmenu", function(e){e.preventDefault()});
	var t = document.getElementById(ids[e]);
	videojs(t).ready(function () {
		var t = document.getElementById(ids[e] + "p");
		t.style.display = "", this.on("play", function () {
			t.style.background = "rgb(40,35,35)", $(".video-js").each(function () {
				var t = $(this).attr("id");
				t !== ids[e] && ((this.player.bufferedPercent() > 0 || 2 == this.player.networkState()) && this.player.load(), document.getElementById(t + "p").style.background = "black")
			})
		})
	})
}

function myFunction() {
	if (scrollable) {
		for (var e = curpos; e < curpos + 9; e++) {
			if (e >= ids.length) {
				document.querySelector("#loader").style.display = "none", document.getElementById("end-text").className = "", scrollable = !1;
				break
			}
			test_elem = document.getElementById(ids[e] + "p"), "undefined" != typeof test_elem && null != test_elem ? document.getElementById(ids[e] + "p").style.display = "" : createsingle(e)
		}
		curpos = e
	}
}

function myFunction_search() {
	if (scrollable) {
		for (var e = curpos_s; e < curpos_s + 9; e++) {
			if (e >= found_list.length) {
				document.querySelector("#loader").style.display = "none", document.getElementById("end-text").className = "", curpos_s = e, scrollable = !1;
				break
			}
			test_elem = document.getElementById(ids[found_list[e]] + "p"), "undefined" != typeof test_elem && null != test_elem ? document.getElementById(ids[found_list[e]] + "p").style.display = "" : createsingle(found_list[e])
		}
		curpos_s = e
	}
}

function play_vid() {
	document.getElementById("bg_video").play()
}

function handleSearchEvents() {
	var e = document.getElementById("myInput");
	document.getElementById("search-icon").addEventListener("click", function () {
		bar_on_screen ? (e.blur(), bar_on_screen = !1) : (e.focus(), bar_on_screen = !0)
	}), e.addEventListener("focus", function () {
		bar_on_screen = !0, "" == e.value && (search_mode = !1, document.querySelector("#loader").style.display = "")
	}), e.addEventListener("blur", function () {
		"" != e.value ? search_mode = !0 : "" == e.value && (search_mode = !1, document.querySelector("#loader").style.display = "")
	}), e.addEventListener("keyup", function () {
		programScroll = !0, bar_on_screen = !0, "" == e.value ? (search_mode = !1, document.querySelector("#loader").style.display = "") : search_mode = !0
	})
}

function createsingle(e) {
	var t = document.createElement("div");
	t.className = "col-md-4", t.style = "display:none;", t.id = ids[e] + "p";
	var n = document.createElement("div");
	n.className = "portfolio-item";
	var l = document.createElement("div");
	l.className = "image";
	var o = document.createElement("div");
	o.className = "thumb";
	var s = document.createElement("div");
	s.className = "hover-content", s.style = "pointer-events:none;", s.id = ids[e] + "h", s.innerHTML = '<h1 style="margin-top:20px;"><em>' + atob(vid_list[e]).substring(7, atob(vid_list[e]).length - 4).replace(/\./g, " ") + "</em></h1><p>Your awesome subtitle goes here</p>";
	var d = document.createElement("video-js");
	d.className = "video-js vjs-theme-fantasy", d.style = "outline:none;", d.id = ids[e], rand_img = Math.floor(4 * Math.random()), chance = Math.random(), 0 == rand_img && chance <= .5 ? d.poster = "thumbs" + atob(vid_list[e]).substring(6) + ".jpg" : 0 == rand_img ? d.poster = "thumbs" + atob(vid_list[e]).substring(6) + ".jpg" : d.poster = "thumbs" + atob(vid_list[e]).substring(6) + "_" + rand_img.toString() + ".jpg";
	var a = document.createElement("source");
	a.type = atob(mime_list[e]), a.src = atob(vid_list[e]), d.appendChild(a), l.appendChild(d), o.appendChild(s), n.appendChild(l), n.appendChild(o), t.appendChild(n), document.getElementById("video_table").appendChild(t);
	var i = document.getElementById(ids[e]);
	func_add = videojs(i, {
		fill: !0,
		muted: !0,
		controls: !0,
		preload: "none",
		aspectRatio: "16:9",
		playbackRates: [.5, 1, 1.5, 2],
		controlBar: {
			pictureInPictureToggle: !1
		}
	}), func_add.ready(function () {
		this.mobileUi(), this.hotkeys({
			volumeStep: .1,
			seekStep: 5,
			enableModifiersForNumbers: !1
		}), this.seekButtons({
			forward: 30,
			back: 10,
			backIndex: 0
		})
	}), addFunctionalities(e)
}

function loadAll() {
	var e, t, n;
	scrollable = !0;
	var l = 0;
	if (e = document.getElementById("myInput").value.toUpperCase(), found_list_temp = [], 0 == e.length && (found_list_temp = []), e.length >= 0) {
		for (t = 0; t < vid_list.length; t++) n = atob(vid_list[t]).substring(2, atob(vid_list[t]).length - 4).replace(/\./g, " "), tagValue = atob(tag_list[t]), n.toUpperCase().indexOf(e) > -1 || tagValue.toUpperCase().indexOf(e) > -1 ? (l += 1, document.getElementById("no-results").style.display = "none", found_list_temp.push(t)) : (0 == l && (document.getElementById("end-text").className = "nodisp", document.querySelector("#loader").style.display = "none", document.getElementById("no-results").style.display = ""), void 0 !== (s = document.getElementById(ids[t] + "p")) && null != s && (s.style.display = "none"));
		var o = 0;
		if ((found_list = found_list_temp).length > 0) {
			for (; o < found_list.length && !(o > 8); o++) {
				var s;
				void 0 !== (s = document.getElementById(ids[found_list[o]] + "p")) && null != s ? document.getElementById(ids[found_list[o]] + "p").style.display = "" : void 0 !== s && null != s || (createsingle(found_list[o]), document.getElementById(ids[found_list[o]] + "p").style.display = "")
			}
			if(o<9){document.querySelector("#loader").style.display = "none";document.getElementById("end-text").className = "";}
			curpos_s = o
		}
	}
	cur_ofset = $(".container-fluid").offset().top, (cur_ofset < 79 || cur_ofset > 81) && $("body").animate({
		scrollTop: window.innerHeight - 80
	}, 500)
}
document.addEventListener("DOMContentLoaded", function () {
	window.HELP_IMPROVE_VIDEOJS = !1, jQuery(document).ready(function (e) {
		"use strict";
		e("a.scrollTo").on("click", function (t) {
			t.preventDefault();
			var n = e(this).attr("data-scrollTo");
			return e("a.scrollTo").each(function () {
				n == e(this).attr("data-scrollTo") ? e(this).addClass("active") : e(this).removeClass("active")
			}), e("body, html").animate({
				scrollTop: window.innerHeight - 80
			}, 500), !1
		})
	})
}), $(function () {
	myFunction(), handleSearchEvents(), $(".preload").each(function (e, t) {
		setTimeout(function () {
			$(t).removeClass("preload"), $(t).addClass("afterload")
		}, 10)
	});
	var e = document.getElementById("set_index");
	var ico=document.getElementById("scicon");
	e.style.zIndex = "300", e.style.display = "",ico.style.display=""
}), $("body").on("scroll",function () {
	var e = $(this).scrollTop();
	if(e > lastScrollTop){
		if($(window).scrollTop() >= $(".container-fluid").offset().top + $(".container-fluid").outerHeight() - window.innerHeight && !search_mode)
		{
			myFunction();
		}
		else if($(window).scrollTop() >= $(".container-fluid").offset().top + $(".container-fluid").outerHeight() - window.innerHeight - 15 && search_mode){ 
			myFunction_search();
		}
		if($(".container-fluid").offset().top < 0)
		{
			 	hideEvents();
		}
	}
		else
			 		{
			 			unhideEvents();
			 		} 
		
			 			lastScrollTop = e;
}), $(window).on("orientationchange", function () {
	if (window.screen.orientation.type = "landscape-primary") {
		const t = document.querySelectorAll(".video-js");
		for (var e = 0; e < t.length; e++)
			if (0 == t[e].player.paused()) try {
				t[e].requestFullscreen ? t[e].requestFullscreen() : t[e].mozRequestFullScreen ? t[e].mozRequestFullScreen() : t[e].webkitRequestFullscreen ? t[e].webkitRequestFullscreen() : t[e].msRequestFullscreen && t[e].msRequestFullscreen()
			} catch (e) {
				alert(err)
			}
	}
});
function hideEvents(){
	if(!$("nav").hasClass("hidden"))
		$("nav").addClass("hidden");
	if(!$("video").get(0).paused){
		$("video").get(0).pause();
	}
}
function unhideEvents(){
	if($("nav").hasClass("hidden"))
		$("nav").removeClass("hidden");
	if($("video").get(0).paused){
		$("video").get(0).play();
	}
}
