jQuery.getMultipleJSON = function(){
  return jQuery.when.apply(jQuery, jQuery.map(arguments, function(jsonfile){
    return jQuery.getJSON(jsonfile);
  })).then(function(){
    var def = jQuery.Deferred();
    return def.resolve.apply(def, jQuery.map(arguments, function(response){
      return response[0];
    }));
  });
};

var viewPage = null;
var viewInfo = null;
var viewAnalysis = null;
var viewCluster = null;

function search(specPageUrl, specInfoUrl, specAnalysisUrl, specClusterUrl) {
    $.getMultipleJSON(specPageUrl, specInfoUrl, specAnalysisUrl)
    .fail(function(jqxhr, textStatus, error){})
    .done(function(specPage, specInfo, specAnalysis) {
        specPage = vega.parse(specPage);
        specInfo = vega.parse(specInfo);
        specAnalysis = vega.parse(specAnalysis);

        viewPage = new vega.View(specPage).logLevel(vega.Warn).renderer('svg').initialize('#page').hover();
        viewInfo = new vega.View(specInfo).logLevel(vega.Warn).renderer('svg').initialize('#info').hover();
        viewAnalysis = new vega.View(specAnalysis).logLevel(vega.Warn).renderer('svg').initialize('#stats').hover();
        viewPage.runAsync();
        viewInfo.runAsync();
        viewAnalysis.runAsync();

        vegaEmbed('#cluster', specClusterUrl).then(function(result) {
            viewCluster = result.view;
            viewCluster.addEventListener('click', function (evt, src) {
                $('#page image').attr('href', '/page/' + src.datum.name + '.png');
                $(window).trigger('resize');
            })
        }).catch(console.error);
    })
}
