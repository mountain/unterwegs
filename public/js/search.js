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
var viewAnalysis = null;
var viewCluster = null;

function search(specPageUrl, specAnalysisUrl, specClusterUrl) {
    $.getMultipleJSON(specPageUrl, specAnalysisUrl)
    .fail(function(jqxhr, textStatus, error){})
    .done(function(specPage, specAnalysis) {
        specPage = vega.parse(specPage);
        specAnalysis = vega.parse(specAnalysis);

        viewPage = new vega.View(specPage).logLevel(vega.Warn).renderer('svg').initialize('#page').hover();
        viewAnalysis = new vega.View(specAnalysis).logLevel(vega.Warn).renderer('svg').initialize('#stats').hover();
        viewPage.runAsync();
        viewAnalysis.runAsync();

        vegaEmbed('#cluster', specClusterUrl).then(function(result) {
            viewCluster = result.view;
            viewCluster.addEventListener('click', function (evt, src) {
                var pid = src.datum.name;
                var q = window.location.pathname.split('/')[2];

                $('#page image').attr('href', '/page/' + pid + '.png');
                $('#page image').attr('width', 760);
                $('#page image').wrap("<a href='/page/'" + pid + "></a>");

                var urlFrequency = '/data/' + q + '/' + pid + '/frequency.json';
                $.getJSON(urlFrequency)
                .fail(function(jqxhr, textStatus, error){
                    console.error(error)
                }).done(function(dataFreq) {
                    viewAnalysis.data('frequency', dataFreq);
                    viewAnalysis = viewAnalysis.renderer('svg').initialize('#stats').hover();
                    viewAnalysis.runAsync();
                });

                $(window).trigger('resize');
            })

        }).catch(console.error);
    })
}
