function detect_rank_a(ranks,a,team_name){
	var txt = a.text();
	var len = ranks.length;
	for(var k=0;k<len;k++){
		if(txt.indexOf(ranks[k].text)!=-1){
			if(team_name==ranks[k].text){
				continue;
			}
			ranks[k].link.attr("style","color:red;");
		}
	}
}
function detect_rank_b(ranks,a,team_name){
	var txt = a.text();
	var len = ranks.length;
	for(var k=0;k<len;k++){
		if(txt.indexOf(ranks[k].text)!=-1){
			if(team_name==ranks[k].text){
				continue;
			}
			style = ranks[k].link.attr("style");
			if(style=="color:red;"){
				ranks[k].link.attr("style","color:green;font-weight:bolder;");
			}else{
				ranks[k].link.attr("style","color:blue;");
			}
		}
	}
}
function _trim(text){
	return text.replace(/\s+/g, "");
}
$(document).ready(function(){
	var team_names = [];
	var team_names_lins = $(".team_name");
	$.each(team_names_lins,function(i,e){
		team_names.push(_trim($(e).text()));
	});
	console.log(team_names);
	var ranks = [];
	var ranks_a = $("#rank_box a")
	$.each(ranks_a,function(i,e){
		if($(e).attr("href").indexOf("team_data.php?teamid=")!=-1){
			var text = $(e).text().trim();
			text = _trim(text);
			obj = {};
			obj.text = text;
			obj.link = $(e);
			ranks.push(obj);
		}
	});
	
	var a_team_links = $("#team_zhanji2_1 a");
	var b_team_links = $("#team_zhanji2_0 a");
	var a_matches_a = [];
	var b_matches_a = [];
	$.each(a_team_links,function(i,a){
		if($(a).attr("href").indexOf("/shuju-")!=-1){
			a_matches_a.push(a);
			detect_rank_a(ranks,$(a),team_names[0]);
		}
	});
	$.each(b_team_links,function(i,a){
		if($(a).attr("href").indexOf("/shuju-")!=-1){
			b_matches_a.push(a);
			detect_rank_b(ranks,$(a),team_names[1]);
		}
	});
});