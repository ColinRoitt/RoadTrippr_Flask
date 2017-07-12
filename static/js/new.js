console.log("loaded");
var start1 = function() {
  // document.getElementById('spotify1').style.display = "block";
  document.getElementById('whatis').style.display = "none";
  document.getElementById('googlemaps').style.display = "block";
}

var mainform = function() {
  document.getElementById('googlemaps').style.display = "none";
  document.getElementById('mainform').style.display = "block";
}

var submit = function() {
  document.getElementById('mainform').style.display = "none";
  document.getElementById('thanks').style.display = "block";
  // redirect to new page with correctly parsed url
  x = document.getElementById;
  itemsOfData = [
    document.getElementById('startplace'),
    document.getElementById('endplace'),
    document.getElementById('randomise'),
    document.getElementById('playlistname'),
    document.getElementById('genre'),
    document.getElementById('hated'),
    document.getElementById('explicit'),
    document.getElementById('nonexplicit')
  ];
  checkboxItems = [
    document.getElementById('randomise'), document.getElementById('explicit'), document.getElementById('nonexplicit')
  ];

  url = '/n?';

  itemsOfData.forEach(function(item){
    if(checkboxItems.indexOf(item) != -1){
      url += item.id + '=' + item.checked + '&';
    }else{
      url += item.id + '=' + item.value + '&';
    }
  });
  //console.log(url);
  window.location.replace(url);
}
