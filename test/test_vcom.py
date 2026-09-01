import json

from ..user_files.queryApi import vcom_funny
from ..user_files.queryApi.vcom_funny.webapi import vcom
from . import mock_helper

# https://corpus.vocabulary.com/api/1.0/examples/random.json?maxResults=4&query=good&startOffset=0
json_str_word_good = """{"sentences":[{"corpusId":"LIT","offsets":[41,45],"sentence":"“Not as dangerous as a man with only one good hand and arm.”","volume":{"asin":"0316299435","author":"Jewell Parker Rhodes","corpus":{"id":"LIT","name":"Literature"},"dateAdded":1780435154617,"datePublished":1735689600000,"domain":"F","domains":["F"],"id":6823037,"isbn":"9780316299435","sentenceCount":1210,"title":"Will’s Race for Home","wordCount":14510},"volumeId":6823037,"volumeOffset":850},{"corpusId":"LIT","offsets":[35,39],"sentence":"In San Francisco, Phineas is not a good invalid.","volume":{"asin":"0618494782","author":"John Fleischman","corpus":{"id":"LIT","name":"Literature"},"dateAdded":1780435439849,"datePublished":1235520000000,"domain":"A","domains":["A"],"id":6823038,"isbn":"9780618494781","sentenceCount":707,"title":"Phineas Gage","wordCount":11965},"volumeId":6823038,"volumeOffset":471},{"corpusId":"LIT","offsets":[18,22],"sentence":"“I’ve still got a good hand,” Caesar says ruefully.","volume":{"asin":"0316299435","author":"Jewell Parker Rhodes","corpus":{"id":"LIT","name":"Literature"},"dateAdded":1780435154617,"datePublished":1735689600000,"domain":"F","domains":["F"],"id":6823037,"isbn":"9780316299435","sentenceCount":1210,"title":"Will’s Race for Home","wordCount":14510},"volumeId":6823037,"volumeOffset":623},{"corpusId":"LIT","offsets":[33,37],"sentence":"“Will’s going to do it! You’re a good man, George!”","volume":{"asin":"0316299435","author":"Jewell Parker Rhodes","corpus":{"id":"LIT","name":"Literature"},"dateAdded":1780435154617,"datePublished":1735689600000,"domain":"F","domains":["F"],"id":6823037,"isbn":"9780316299435","sentenceCount":1210,"title":"Will’s Race for Home","wordCount":14510},"volumeId":6823037,"volumeOffset":909}],"totalHits":7706}"""


# https://www.vocabulary.com/dictionary/good
html_str_word_good = """







	
		
	
	

<!DOCTYPE html>
<html lang="en">
<head>	
	<title>Good - Definition, Meaning & Synonyms | Vocabulary.com</title>
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<meta name="google" content="notranslate">
    <meta name="description" content="We all know what good means as an adjective––pleasing, favorable, nice. But did you know that good is also a noun, meaning something that can be sold? This means a shopkeeper’s ideal is to have really good goods." />
	        <meta name="robots" content="noarchive" />
	        <link rel="canonical" href="https://www.vocabulary.com/dictionary/good"/>
	        <meta property="og:title" content="Good - Definition, Meaning &amp; Synonyms"/>
			<meta property="og:site_name" content="Vocabulary.com" />
			<meta property="og:type" content="article" />
			<meta property="og:image" content="https://www.vocabulary.com/images/icons/facebook-75x75.gif" />    
			<meta property="og:description" content="We all know what good means as an adjective––pleasing, favorable, nice. But did you know that good is also a noun, meaning something that can be sold? This means a shopkeeper’s ideal is to have really good goods."/>
    
	<link rel="search" type="application/opensearchdescription+xml" href="https://www.vocabulary.com/search.xml" title="Vocabulary.com" />    
	<link href="https://cdn.vocabulary.com/images/ios-icons/114x114-off5pn.png" rel="apple-touch-icon"/>
	<link href="https://cdn.vocabulary.com/images/favicons/favicon-32x32-2frmtt.png" sizes="32x32" rel="icon" type="image/png"/>
	<link href="https://cdn.vocabulary.com/images/favicons/favicon-16x16-uf6i7e.png" sizes="16x16" rel="icon" type="image/png"/>

	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400;1,700&family=Open+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500;1,600;1,700&display=swap" rel="stylesheet">
	<link href="https://cdn.vocabulary.com/css/header-18eveua.css" rel="stylesheet" type="text/css"/>
	<link href="https://cdn.vocabulary.com/css/main-1knvpzy.css" rel="stylesheet" type="text/css"/>
	<link href="https://cdn.vocabulary.com/css/progress-1x2p62h.css" rel="stylesheet" type="text/css"/>
	<link href="https://cdn.vocabulary.com/css/dictionary-kd1ket.css" rel="stylesheet" type="text/css"/>
	<link href="https://cdn.vocabulary.com/css/achievements-4to21o.css" rel="stylesheet" type="text/css"/>
	<link href="https://cdn.vocabulary.com/css/leaderboards-xxg0un.css" rel="stylesheet" type="text/css"/>
	
	<link href="https://cdn.vocabulary.com/css/fonts/ss-social-circle-e51wc0.css" rel="stylesheet" type="text/css"/>	
	<link href="https://cdn.vocabulary.com/css/fonts/ss-symbolicons-block-67mxq6.css" rel="stylesheet" type="text/css"/>
	<link href="https://cdn.vocabulary.com/css/fonts/ss-standard-5s5b7z.css" rel="stylesheet" type="text/css"/>
	
	<link href="https://cdn.vocabulary.com/css/test-prep-promo-wo7tbr.css" rel="stylesheet" type="text/css"/>
<link href="https://cdn.vocabulary.com/css/marketing-bowl-subscription-7tpx2p.css" rel="stylesheet" type="text/css"/>
<link href="https://cdn.vocabulary.com/css/promote/learner-subscribe-1siu16x.css" rel="stylesheet" type="text/css"/>
<style>
body {
	overflow-y: scroll;
}
</style>
	<script>
	window.onerror = function(message, source, line, col, error){
		try {
			if (window.XMLHttpRequest && line && (!window.lasterr || new Date().getTime() - window.lasterr.getTime() > 10000)) {
				var httpRequest = new XMLHttpRequest();
				httpRequest.open('POST', '/js/error');
				httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
				httpRequest.send('msg=' + encodeURIComponent(JSON.stringify(
					{"msg":message, 
					"src":source, 
					"line":line, 
					"col":col, 
					"err":error
					}
				)));
				window.lasterr = new Date();
			}
		} catch(e){}
	}
	</script>
	
	<script>
		window.dataLayer = window.dataLayer || []; /* GTM Data Layer */
		window.VCOM=(window.VCOM=function(){(VCOM.q=VCOM.q||[]).push(arguments)});
		window.VCOM.__api_server = "https://api.vocabulary.com";
	</script>
	<!-- ReCaptcha V3 -->
	<script src="https://www.google.com/recaptcha/enterprise.js?render=6LeddZEqAAAAAHAYLf9Sz82cN_hk-HFe_coTdqNA"></script>
	
	<script src="https://cdn.vocabulary.com/lib/jquery-1eev1tf.js" type="text/javascript"></script>
	<script src="https://cdn.vocabulary.com/js/module-186xco1.js" type="text/javascript"></script>
	
		<script type="text/javascript">
(function() {
	window.__cmpmode = null;
	
	var cbs = [];
	var status;
    window.__cmp = function(cmd, cb, gdprApplies, consent) {
    	if (cmd === 'getConsentData') {
    		if (status) {
    			cb(status);
    		} else {
    			cbs.push(cb);
    		}
    	} else if (cmd === 'cb') {
    		status = {gdprApplies:gdprApplies, hasGlobalConsent:consent};
    		for (var i = 0; i < cbs.length; i++) {
    			cbs[i](status);
    		}
    	}
	}
    
    var elem = document.createElement('script');
    elem.src = 'https://cdn.vocabulary.com/js/vcom/cmp-558kst.js';
    elem.async = true;
    elem.type = "text/javascript";
    var scpt = document.getElementsByTagName('script')[0];
    scpt.parentNode.insertBefore(elem, scpt);
})();
</script>
<style>
body .cookie-privacy-banner {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	z-index: 9999;
	padding: 1em 0;
	font-size: 90%;
	background: linear-gradient(rgba(51,82,109,.95) 0%,rgba(32,67,98,.95) 100%);
	color: #e0e0e0;
	display: none;
}
body.with-cookie-banner .cookie-privacy-banner {
	display: block;
}
body.with-cookie-banner .page-footer {
	padding-bottom: 18em;
}
.cookie-privacy-banner a {
	color: #e0e0e0;
}
.cookie-privacy-banner p {
	line-height: 125%;
}
.cookie-privacy-banner .i-agree {
	margin-right: 2em;
}
.cookie-privacy-banner .choice {
	font-weight: bold;
}
</style>
	
	<script>
	Module.after(['jquery', 'vcom/base','vcom/usermenu' ],function(){});
	</script>

	<script type="text/javascript">	
	var noresults = false;		
	</script>

	

<script type="module" src="https://cdn.vocabulary.com/js3/mixpanel.bAyToM0F.bundle.js"></script>
<script>
Module.after(['vcom/analytics/mixpanel'], function() {
	window.ga=window.ga||function(){(ga.q=ga.q||[]).push(arguments)};ga.l=+new Date;
	ga('create', 'UA-154986-6', 'auto');
	window.dataLayer = window.dataLayer || [];

	VCOM('gdpr',function(){
		
		var t = document.createElement('script');
		t.async=true;
		t.src='https://www.google-analytics.com/analytics.js';
		document.head.appendChild(t);
		
		
		(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
			new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
			j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
			'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
			})(window,document,'script','dataLayer','GTM-TN79ND');

        // Mixpanel PageView + TimeOnPage tracking
        window.addEventListener('pageshow', function (event) {
            // Mixpanel PageView tracking: use pageshow window event to handle both regular page navigation and bfcache restoration
            try {
                // Store the total number of pageviews of the current browser session
                let sessionPageViewCount = sessionStorage.getItem("session-pageview-count") || 0;
                sessionPageViewCount = Number(sessionPageViewCount) + 1;
                sessionStorage.setItem("session-pageview-count", sessionPageViewCount);
                modules.vcom.analytics.mixpanel.mpPageView(sessionPageViewCount);
            } catch (error) {}

            // TimeOnPage tracking -- part 1 ======
            // Handle the case: user navigates to another path of vocabulary.com for
            // some browsers (e.g., Chrome) that unloads pagehide event listener before it is executed
            try {
                const currentTime = new Date().getTime();
                if (sessionStorage.getItem("timeOnPage-tracked-by-pagehide") !== "true") {
                    const lastPageLoadTime = sessionStorage.getItem("last-pageload-time");
                    const lastPageLoadPath = sessionStorage.getItem("last-pageload-path");
                    if (lastPageLoadTime !== null) {
                        modules.vcom.analytics.mixpanel.mpTimeOnPage((currentTime - lastPageLoadTime) / 1000, lastPageLoadPath);
                    }
                } else {
                    sessionStorage.removeItem("timeOnPage-tracked-by-pagehide");
                }
                sessionStorage.setItem("last-pageload-time", currentTime);
                sessionStorage.setItem("last-pageload-path", window.location.pathname);
            } catch (error) {}
        });

        // TimeOnPage tracking -- part 2 ======
        // Handle the cases: navigate to another path of vocabulary.com, page refreshed, or tab closed
        window.addEventListener('pagehide', (event) => {
            try {
                const lastPageLoadTime = sessionStorage.getItem("last-pageload-time");
                const lastPageLoadPath = sessionStorage.getItem("last-pageload-path");
                // filters out page load from b/f cache, which causes both current and b/f page to fire pagehide listener
                if (event.persisted === false && lastPageLoadTime !== null) {
                    // avoid duplicate TimeOnPage event sent by pageshow event listener
                    sessionStorage.setItem("timeOnPage-tracked-by-pagehide", "true");
                    const currentTime = new Date().getTime();
                    modules.vcom.analytics.mixpanel.mpTimeOnPage((currentTime - lastPageLoadTime) / 1000, lastPageLoadPath);
                    sessionStorage.removeItem("last-pageload-time");
                    sessionStorage.removeItem("last-pageload-path");
                }
            } catch (error) {}
        });
    });
	
	VCOM('auth',function(auth){
		var userType = 'unknown';
		if (auth.validUser) {
			userType = auth.ima || 'unknown';
			ga('set','dimension1',auth.paid?'paid':'free');
			ga('set','dimension2', userType);
			var role = (auth.auth && auth.auth.role) ? auth.auth.role.toLowerCase() : "";
			if (role=='bill' && auth.plan) role = auth.plan;
			if (role) ga('set','dimension3',role);
			if (auth.classes && !auth.classes.empty)  ga('set','dimension4','inclass');
						
			if (window.dataLayer) {
				window.dataLayer.push({
					user_id: auth.auth.uid || '',
					user_type: userType
				});
			}
			// Check if user is in EU and may call backend API to check if user's profile has consentedToGDPR
			const eu = modules.cookie.get('_eu');
			const cookieConsent = modules.cookie.get("cookie_consent");
			// Update db Profile if user is in EU and consentedToGDPR is not set in Profile yet
			if (eu === "1" && auth.auth.consentedToGDPR === undefined && window.sessionStorage.getItem("consentedToGDPRUpdated") === null) {
				// consentedToGDPR is set to true if cookie_consent is "1", false otherwise (null or "0")
				$.post('/account/updateprofileconsentedtogdpr.json', {
					consentedToGDPR: cookieConsent === "1"
				}, function(response) {});
				// Set a session flag to avoid unnecessary consentedToGDPR update calls
				window.sessionStorage.setItem("consentedToGDPRUpdated", "true");
			}
			
		} else {
			userType = 'anonymous';
			ga('set','dimension1','anon');
			if (window.dataLayer) {
				window.dataLayer.push({
					user_type: userType
				});				
			}
			// reset mixpanel instance if no user is logged in + the mp instance is not reset yet
			modules.vcom.analytics.mixpanel.mpUserReset();
		}

		ga('send', 'pageview');
		
		if (window.dataLayer && userType != 'unknown' && userType != 'anonymous') {
			var cks = document.cookie.split(';')
	    	.map(function(v){
	    		return v.split('=');
	    	})
	    	.reduce(function(acc, v) {
	      		acc[decodeURIComponent(v[0].trim())] = decodeURIComponent(v[1].trim());
	      		return acc;
	    	}, {});

			const authMethod = (auth.auth && auth.auth.method) ? auth.auth.method : 'unknown';
			if (cks.gtag_signup) {
				window.dataLayer.push({
					event: 'sign_up',
					method: cks.gtag_signup || 'unknown'
				});
				document.cookie = ("gtag_signup=; domain=vocabulary.com; max-age=0; path=/");
				
				ga('send','event','Signup',userType);
			}
			
			if (cks.gtag_login) {
				window.dataLayer.push({
					event: 'login',
					method: authMethod
				});
				document.cookie = ("gtag_login=; domain=vocabulary.com; max-age=0; path=/");
				modules.vcom.analytics.mixpanel.mpLoginSuccessEvent(authMethod);
			}
		}
	});	
});
</script>
</head>
<body class=" with-top-tab with-tab-dictionary top-section-none with-light-header">
<div class="body-wrapper">
<a href="#hdr-word-area" class="skip-to-main-content">SKIP TO CONTENT</a>
<header class="page-header noselect" role="banner"><div class="limited-width"><nav class="main">
		<a href="/" title="Vocabulary.com" class="logo" ><img src="https://cdn.vocabulary.com/images/header/logo-1wobq9i.png" alt="Vocabulary.com" class="screen-only"/><img src="https://cdn.vocabulary.com/images/logo-sar2cf.svg" alt="" class="print-only"/></a>
		<div class="logininfo"></div><button role="button" aria-pressed="false" aria-label="navigation menu" class="hamburger menu"><span class="rows"></span></button></nav><nav class="tabs">
 		<ul>
			
			<li title="Look up a word" class="dictTab selected empty"><a href="/dictionary/"><span>Dictionary</span></a></li><li title="Find a Vocabulary List" class="listsTab"><a href="/lists/"><span>Vocabulary Lists</span></a></li><li title="VocabTrainer™" class="vocabTrainerTab"><a href="/vocabtrainer/"><span>VocabTrainer™</span></a></li></ul></nav><div class="achievements"></div><div class="recent"></div></div></header>
<div class="fixed-tray">
	<header class="banner" style="z-index:auto;">
 		<div class="wrapper">
 			<div class="limited-width">
 				<div class="smart-search-app"></div>
				<script type="module" src="https://cdn.vocabulary.com/js3/smart-search.Bm_4fML5.bundle.js"></script><link href="https://cdn.vocabulary.com/js3/smart-search.PEDoEohX.bundle.css" rel="stylesheet" type="text/css"><link href="https://cdn.vocabulary.com/js3/SmartSearchContent.BvDGeMSd.bundle.css" rel="stylesheet" type="text/css">
			</div>
		</div>
	 </header>
</div>
<div id="page" class="page">
	<div
		class="pageContent clearfloat "
		id="pageContent"
		tabindex="-1"
	>









	<div
		class="wordPage blurbed clearfloat content-wrapper" 
   		data-lang="en"
		data-word="good"    
   		data-maxfilterlevel="0"
   		data-learnable="false"
   		data-hasimage="false"
		data-next="goodbye"
		data-prev="goo"><script type="application/ld+json">{"@context":"https://schema.org/","@type":"DefinedTerm","@id":"https://www.vocabulary.com/dictionary/good","name":"good","description":"Good comes from an old German root for gathering, and in its original sense it means that something fits well. If something is good for you, it fits you well, or is healthy for you to eat. A long walk through a crowded city is good for someone who likes people-watching, but if you are a misanthrope and you hate people, that wouldn't be so good. If food has spoiled, it’s no longer good.","inDefinedTermSet":"https://www.vocabulary.com/dictionary/"}</script>
 	<div class="centeredContent">
	
	
	
		<div class="definitionsContainer">		
		
		<div class="definition-columns">
		<div class="col-1">
		
			<div class="word-area">
			<script type="text/javascript">
			Module.after(['jquery'], function(){
				jQuery(function($){
					$('.pron-audio').parent().click(function(){
						$(this).children(".pron-audio").get(0).play();
					});
				});
			});
			</script>
				
				
				<!-- dictionary v2 -->
				<div class="header-container">
					<h1
						aria-label="dictionary page of the word good"
						id="hdr-word-area">
						good
					</h1>
					<span style="display:flex;column-gap:8px;">
						<vcom:addtolist word="good" lang="en" label="Add to list"></vcom:addtolist>
						
							<div class="box-init-share-copy-url"><!-- --></div>
							<script type="module" src="https://cdn.vocabulary.com/js3/share-copy-url.BicEuqWZ.bundle.js"></script><link href="https://cdn.vocabulary.com/js3/entry.DGbu-saO.bundle.css" rel="stylesheet" type="text/css">
						
					</span>
				</div>
				
				<div class="ipa-section">
				
					
					<div class="ipa-with-audio">
						<div class="us-flag-icon"></div>
						
							
								<a data-audio="G/1C361RWL0RWKM" class="audio"></a>
							
							
						
						
						<span class="span-replace-h3">/gʊd/</span>
						
					</div>
						
					
					
						<div class="ipa-with-audio">
						<div class="uk-flag-icon"></div>
							
							
							
								
									<a class="audio"><audio class="pron-audio" src="https://sd-pronunciation-processed-videos.sdcdns.com/desktop/lang_en_pron_4348_speaker_8_syllable_all_version_50.mp4"></audio></a>
								
							
						
						
						<span class="span-replace-h3">
							/gʊd/
						</span>
						
						</div>
					
					<a class="ipa-guide" href="/resources/ipa-pronunciation/">IPA guide</a>
				</div>
				
				
			
				
				
					<p class="word-forms">Other forms: <b>better; best; goods</b></p>
				
				<p class="short">We all know what <i>good</i> means as an adjective––pleasing, favorable, nice. But did you know that <i>good</i> is also a noun, meaning something that can be sold? This means a shopkeeper’s ideal is to have really <i>good goods</i>.</p>
				<p class="long"><i>Good</i> comes from an old German root for gathering, and in its original sense it means that something fits well. If something is good for you, it fits you well, or is healthy for you to eat. A long walk through a crowded city is good for someone who likes people-watching, but if you are a misanthrope and you hate people, that wouldn't be so good. If food has spoiled, it’s no longer good.</p>
			</div>		
			
			
			<div class="word-definitions">
				<div class="label">Definitions of <span class="word">good</span> </div>
				<ol>
				
				
				<li class="sense pos_a ord1 sord1" id="s102045">
					<div class="definition"><div name="s102045" class="pos-icon">adjective</div>
					 having desirable or positive qualities especially those suitable for a thing specified</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;<strong>good</strong> news from the hospital&#8221;</div>
					
						<div class="example">&#8220;a <strong>good</strong> report card&#8221;</div>
					
						<div class="example">&#8220;when she was <strong>good</strong> she was very very good&#8221;</div>
					
						<div class="example">&#8220;a <strong>good</strong> knife is one good for cutting&#8221;</div>
					
						<div class="example">&#8220;this stump will make a <strong>good</strong> picnic table&#8221;</div>
					
						<div class="example">&#8220;a <strong>good</strong> check&#8221;</div>
					
						<div class="example">&#8220;a <strong>good</strong> joke&#8221;</div>
					
						<div class="example">&#8220;a <strong>good</strong> exterior paint&#8221;</div>
					
						<div class="example">&#8220;a <strong>good</strong> secretary&#8221;</div>
					
						<div class="example">&#8220;a <strong>good</strong> dress for the office&#8221;</div>
					
					
					


					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/best" class="word">best</a>
					
					
						<div class="definition">(superlative of `good') having the most positive qualities</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/better" class="word">better</a>
					
					
						<div class="definition">(comparative of `good') superior to another (of the same class or set or kind) in excellence or quality or desirability or suitability; more highly skilled than another</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/favorable" class="word">favorable</a>, 
					
						<a href="/dictionary/favourable" class="word">favourable</a>
					
					
						<div class="definition">encouraging or approving or pleasing</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/bang-up" class="word">bang-up</a>, 
					
						<a href="/dictionary/bully" class="word">bully</a>, 
					
						<a href="/dictionary/corking" class="word">corking</a>, 
					
						<a href="/dictionary/cracking" class="word">cracking</a>, 
					
						<a href="/dictionary/dandy" class="word">dandy</a>, 
					
						<a href="/dictionary/great" class="word">great</a>, 
					
						<a href="/dictionary/groovy" class="word">groovy</a>, 
					
						<a href="/dictionary/keen" class="word">keen</a>, 
					
						<a href="/dictionary/neat" class="word">neat</a>, 
					
						<a href="/dictionary/nifty" class="word">nifty</a>, 
					
						<a href="/dictionary/not bad" class="word">not bad</a>, 
					
						<a href="/dictionary/peachy" class="word">peachy</a>, 
					
						<a href="/dictionary/slap-up" class="word">slap-up</a>, 
					
						<a href="/dictionary/smashing" class="word">smashing</a>, 
					
						<a href="/dictionary/swell" class="word">swell</a>
					
					
						<div class="definition">very good</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/good enough" class="word">good enough</a>
					
					
						<div class="definition">adequately good for the circumstances</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/goodish" class="word">goodish</a>
					
					
						<div class="definition">moderately good of its kind</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/hot" class="word">hot</a>
					
					
						<div class="definition">very good; often used in the negative</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/redeeming" class="word">redeeming</a>
					
					
						<div class="definition">compensating for some fault or defect</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/acceptable" class="word">acceptable</a>, 
					
						<a href="/dictionary/satisfactory" class="word">satisfactory</a>
					
					
						<div class="definition">meeting requirements</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/solid" class="word">solid</a>
					
					
						<div class="definition">characterized by good substantial quality</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/superb" class="word">superb</a>
					
					
						<div class="definition">surpassingly good</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/well behaved" class="word">well behaved</a>, 
					
						<a href="/dictionary/well-behaved" class="word">well-behaved</a>
					
					
						<div class="definition">(usually of children) someone who behaves in a manner that the speaker believes is correct</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/obedient" class="word">obedient</a>
					
					
						<div class="definition">dutifully complying with the commands or instructions of those in authority</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/respectable" class="word">respectable</a>
					
					
						<div class="definition">characterized by socially or conventionally acceptable morals</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
						<div class="more-info-section">
							<a class="more-info-expander" href="#0"><span class="expand-text">see more</span><span class="hide-text">see less</span><span class="carat-icon"></span></a>
							<div class="more-info">
								



	

	<div class="div-replace-dl instances">
		<span class="detail">antonyms:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/bad" class="word">bad</a>
					
					
						<div class="definition">having undesirable or negative qualities</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/worst" class="word">worst</a>
					
					
						<div class="definition">(superlative of `bad') most wanting in quality or value or condition</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/worse" class="word">worse</a>
					
					
						<div class="definition">(comparative of `bad') inferior to another in quality or condition or desirability</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/unfavorable" class="word">unfavorable</a>, 
					
						<a href="/dictionary/unfavourable" class="word">unfavourable</a>
					
					
						<div class="definition">not encouraging or approving or pleasing</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/abominable" class="word">abominable</a>, 
					
						<a href="/dictionary/abysmal" class="word">abysmal</a>, 
					
						<a href="/dictionary/atrocious" class="word">atrocious</a>, 
					
						<a href="/dictionary/awful" class="word">awful</a>, 
					
						<a href="/dictionary/dreadful" class="word">dreadful</a>, 
					
						<a href="/dictionary/painful" class="word">painful</a>, 
					
						<a href="/dictionary/terrible" class="word">terrible</a>, 
					
						<a href="/dictionary/unspeakable" class="word">unspeakable</a>, 
					
						<a href="/dictionary/vile" class="word">vile</a>
					
					
						<div class="definition">exceptionally bad or displeasing</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/corked" class="word">corked</a>, 
					
						<a href="/dictionary/corky" class="word">corky</a>
					
					
						<div class="definition">(of wine) tainted in flavor by a cork containing excess tannin</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/deplorable" class="word">deplorable</a>, 
					
						<a href="/dictionary/distressing" class="word">distressing</a>, 
					
						<a href="/dictionary/lamentable" class="word">lamentable</a>, 
					
						<a href="/dictionary/pitiful" class="word">pitiful</a>, 
					
						<a href="/dictionary/sad" class="word">sad</a>, 
					
						<a href="/dictionary/sorry" class="word">sorry</a>
					
					
						<div class="definition">bad; unfortunate</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/fearful" class="word">fearful</a>, 
					
						<a href="/dictionary/frightful" class="word">frightful</a>
					
					
						<div class="definition">extremely distressing</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/hard" class="word">hard</a>, 
					
						<a href="/dictionary/tough" class="word">tough</a>
					
					
						<div class="definition">unfortunate or hard to bear</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/hopeless" class="word">hopeless</a>
					
					
						<div class="definition">(informal to emphasize how bad it is) beyond hope of management or reform</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/horrid" class="word">horrid</a>
					
					
						<div class="definition">exceedingly bad</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/icky" class="word">icky</a>, 
					
						<a href="/dictionary/lousy" class="word">lousy</a>, 
					
						<a href="/dictionary/rotten" class="word">rotten</a>, 
					
						<a href="/dictionary/stinking" class="word">stinking</a>, 
					
						<a href="/dictionary/stinky" class="word">stinky</a>
					
					
						<div class="definition">very bad</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/ill" class="word">ill</a>
					
					
						<div class="definition">distressing</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/incompetent" class="word">incompetent</a>, 
					
						<a href="/dictionary/unskilled" class="word">unskilled</a>
					
					
						<div class="definition">not doing a good job</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/mediocre" class="word">mediocre</a>
					
					
						<div class="definition">poor to middling in quality</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/naughty" class="word">naughty</a>
					
					
						<div class="definition">badly behaved</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/negative" class="word">negative</a>
					
					
						<div class="definition">having the quality of something harmful or unpleasant</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/poor" class="word">poor</a>
					
					
						<div class="definition">unsatisfactory</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/pretty" class="word">pretty</a>
					
					
						<div class="definition">(used ironically) unexpectedly bad</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/no-good" class="word">no-good</a>, 
					
						<a href="/dictionary/rubber" class="word">rubber</a>
					
					
						<div class="definition">returned for lack of funds</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/severe" class="word">severe</a>
					
					
						<div class="definition">very bad in degree or extent</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/swingeing" class="word">swingeing</a>
					
					
						<div class="definition">severe; punishingly bad</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/uncool" class="word">uncool</a>
					
					
						<div class="definition">(spoken slang) unfashionable and boring</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/unfavorable" class="word">unfavorable</a>, 
					
						<a href="/dictionary/unfavourable" class="word">unfavourable</a>
					
					
						<div class="definition">not favorable</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/unsuitable" class="word">unsuitable</a>
					
					
						<div class="definition">not conducive to good moral development</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/evil" class="word">evil</a>
					
					
						<div class="definition">morally bad or wrong</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/disobedient" class="word">disobedient</a>
					
					
						<div class="definition">not obeying or complying with commands of those in authority</div>
					
				</div>			
			
		
		
			<div class="div-replace-dd more">
				<a href="javascript:void(0);" class="expander" >show more antonyms...</a>
			</div>
		
	</div>			

								
								
								


								
								
								


								
								


								


							</div>
						</div>
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord1 sord2" id="s104993">
					<div class="definition"><div name="s104993" class="pos-icon">adjective</div>
					 most suitable or right for a particular purpose</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;a <strong>good</strong> time to plant tomatoes&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/right" class="word">right</a>, 
				
					<a href="/dictionary/ripe" class="word">ripe</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/opportune" class="word">opportune</a>
					
					
						<div class="definition">suitable or at a time that is suitable or advantageous especially for a particular purpose</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord2 sord1" id="s102284">
					<div class="definition"><div name="s102284" class="pos-icon">adjective</div>
					 in excellent physical condition</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;<strong>good</strong> teeth&#8221;</div>
					
						<div class="example">&#8220;I still have one <strong>good</strong> leg&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/sound" class="word">sound</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/healthy" class="word">healthy</a>
					
					
						<div class="definition">having or indicating good health in body or mind; free from infirmity or disease</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord3 sord1" id="s102260">
					<div class="definition"><div name="s102260" class="pos-icon">adjective</div>
					 tending to promote physical well-being; beneficial to health</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;a <strong>good</strong> night's sleep&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/salutary" class="word">salutary</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/healthful" class="word">healthful</a>
					
					
						<div class="definition">conducive to good health of body or mind</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord3 sord2" id="s96222">
					<div class="definition"><div name="s96222" class="pos-icon">adjective</div>
					 promoting or enhancing well-being</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;the experience was <strong>good</strong> for her&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/beneficial" class="word">beneficial</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/advantageous" class="word">advantageous</a>
					
					
						<div class="definition">giving an advantage</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord4 sord1" id="s104578">
					<div class="definition"><div name="s104578" class="pos-icon">adjective</div>
					 agreeable or pleasing</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;we all had a <strong>good</strong> time&#8221;</div>
					
						<div class="example">&#8220;<strong>good</strong> manners&#8221;</div>
					
					
					


					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/nice" class="word">nice</a>
					
					
						<div class="definition">pleasant or pleasing or agreeable in nature or appearance</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord4 sord2" id="s105812">
					<div class="definition"><div name="s105812" class="pos-icon">adjective</div>
					 capable of pleasing</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;<strong>good</strong> looks&#8221;</div>
					
					
					


					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/pleasing" class="word">pleasing</a>
					
					
						<div class="definition">giving pleasure and satisfaction</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord5 sord1" id="s108189">
					<div class="definition"><div name="s108189" class="pos-icon">adjective</div>
					 having or showing knowledge and skill and aptitude</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;a <strong>good</strong> mechanic&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/adept" class="word">adept</a>, 
				
					<a href="/dictionary/expert" class="word">expert</a>, 
				
					<a href="/dictionary/practiced" class="word">practiced</a>, 
				
					<a href="/dictionary/proficient" class="word">proficient</a>, 
				
					<a href="/dictionary/skilful" class="word">skilful</a>, 
				
					<a href="/dictionary/skillful" class="word">skillful</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/skilled" class="word">skilled</a>
					
					
						<div class="definition">having or showing or requiring special skill</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord6 sord1" id="s103154">
					<div class="definition"><div name="s103154" class="pos-icon">adjective</div>
					 appealing to the mind</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;<strong>good</strong> music&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/serious" class="word">serious</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/intellectual" class="word">intellectual</a>
					
					
						<div class="definition">appealing to or using the intellect</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord7 sord1" id="s102077">
					<div class="definition"><div name="s102077" class="pos-icon">adjective</div>
					 morally admirable</div>
					<div class="defContent">
					
					
					
					


					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/angelic" class="word">angelic</a>, 
					
						<a href="/dictionary/angelical" class="word">angelical</a>, 
					
						<a href="/dictionary/beatific" class="word">beatific</a>, 
					
						<a href="/dictionary/sainted" class="word">sainted</a>, 
					
						<a href="/dictionary/saintlike" class="word">saintlike</a>, 
					
						<a href="/dictionary/saintly" class="word">saintly</a>
					
					
						<div class="definition">marked by utter benignity; resembling or befitting an angel or saint</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/goody-goody" class="word">goody-goody</a>
					
					
						<div class="definition">affectedly or smugly good or self-righteous</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/redeeming" class="word">redeeming</a>, 
					
						<a href="/dictionary/redemptive" class="word">redemptive</a>, 
					
						<a href="/dictionary/saving" class="word">saving</a>
					
					
						<div class="definition">bringing about salvation or redemption from sin</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/white" class="word">white</a>
					
					
						<div class="definition">benevolent; without malicious intent</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/moral" class="word">moral</a>
					
					
						<div class="definition">concerned with principles of right and wrong or conforming to standards of behavior and character based on those principles</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/right" class="word">right</a>
					
					
						<div class="definition">in conformance with justice or law or morality</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/righteous" class="word">righteous</a>
					
					
						<div class="definition">characterized by or proceeding from accepted standards of morality or justice</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/virtuous" class="word">virtuous</a>
					
					
						<div class="definition">morally excellent</div>
					
				</div>			
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/worthy" class="word">worthy</a>
					
					
						<div class="definition">having worth or merit or value; being honorable or admirable</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
						<div class="more-info-section">
							<a class="more-info-expander" href="#0"><span class="expand-text">see more</span><span class="hide-text">see less</span><span class="carat-icon"></span></a>
							<div class="more-info">
								



	

	<div class="div-replace-dl instances">
		<span class="detail">antonyms:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/evil" class="word">evil</a>
					
					
						<div class="definition">morally bad or wrong</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/bad" class="word">bad</a>
					
					
						<div class="definition">having undesirable or negative qualities</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/atrocious" class="word">atrocious</a>, 
					
						<a href="/dictionary/flagitious" class="word">flagitious</a>, 
					
						<a href="/dictionary/grievous" class="word">grievous</a>, 
					
						<a href="/dictionary/monstrous" class="word">monstrous</a>
					
					
						<div class="definition">shockingly brutal or cruel</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/bad" class="word">bad</a>
					
					
						<div class="definition">characterized by wickedness or immorality</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/dark" class="word">dark</a>, 
					
						<a href="/dictionary/sinister" class="word">sinister</a>
					
					
						<div class="definition">stemming from evil characteristics or forces; wicked or dishonorable</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/corruptive" class="word">corruptive</a>, 
					
						<a href="/dictionary/perversive" class="word">perversive</a>, 
					
						<a href="/dictionary/pestiferous" class="word">pestiferous</a>
					
					
						<div class="definition">tending to corrupt or pervert</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/demonic" class="word">demonic</a>, 
					
						<a href="/dictionary/diabolic" class="word">diabolic</a>, 
					
						<a href="/dictionary/diabolical" class="word">diabolical</a>, 
					
						<a href="/dictionary/fiendish" class="word">fiendish</a>, 
					
						<a href="/dictionary/hellish" class="word">hellish</a>, 
					
						<a href="/dictionary/infernal" class="word">infernal</a>, 
					
						<a href="/dictionary/satanic" class="word">satanic</a>, 
					
						<a href="/dictionary/unholy" class="word">unholy</a>
					
					
						<div class="definition">extremely evil or cruel; expressive of cruelty or befitting hell</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/despicable" class="word">despicable</a>, 
					
						<a href="/dictionary/slimy" class="word">slimy</a>, 
					
						<a href="/dictionary/ugly" class="word">ugly</a>, 
					
						<a href="/dictionary/unworthy" class="word">unworthy</a>, 
					
						<a href="/dictionary/vile" class="word">vile</a>, 
					
						<a href="/dictionary/worthless" class="word">worthless</a>, 
					
						<a href="/dictionary/wretched" class="word">wretched</a>
					
					
						<div class="definition">morally reprehensible</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/devilish" class="word">devilish</a>, 
					
						<a href="/dictionary/diabolic" class="word">diabolic</a>, 
					
						<a href="/dictionary/diabolical" class="word">diabolical</a>, 
					
						<a href="/dictionary/mephistophelean" class="word">mephistophelean</a>, 
					
						<a href="/dictionary/mephistophelian" class="word">mephistophelian</a>
					
					
						<div class="definition">showing the cunning or ingenuity or wickedness typical of a devil</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/evil-minded" class="word">evil-minded</a>
					
					
						<div class="definition">having evil thoughts or intentions</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/immoral" class="word">immoral</a>
					
					
						<div class="definition">deliberately violating accepted principles of right and wrong</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/offensive" class="word">offensive</a>
					
					
						<div class="definition">unpleasant or disgusting especially to the senses</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/wrong" class="word">wrong</a>
					
					
						<div class="definition">contrary to conscience or morality or law</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/unrighteous" class="word">unrighteous</a>
					
					
						<div class="definition">not righteous</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/wicked" class="word">wicked</a>
					
					
						<div class="definition">morally bad in principle or practice</div>
					
				</div>			
			
		
		
			<div class="div-replace-dd more">
				<a href="javascript:void(0);" class="expander" >show more antonyms...</a>
			</div>
		
	</div>			

								
								
								


								
								
								


								
								


								


							</div>
						</div>
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord7 sord2" id="s107042">
					<div class="definition"><div name="s107042" class="pos-icon">adjective</div>
					 of moral excellence</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;a genuinely <strong>good</strong> person&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/just" class="word">just</a>, 
				
					<a href="/dictionary/upright" class="word">upright</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/righteous" class="word">righteous</a>
					
					
						<div class="definition">characterized by or proceeding from accepted standards of morality or justice</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord8 sord1" id="s106743">
					<div class="definition"><div name="s106743" class="pos-icon">adjective</div>
					 deserving of esteem and respect</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;ruined the family's <strong>good</strong> name&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/estimable" class="word">estimable</a>, 
				
					<a href="/dictionary/honorable" class="word">honorable</a>, 
				
					<a href="/dictionary/respectable" class="word">respectable</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/reputable" class="word">reputable</a>
					
					
						<div class="definition">having a good reputation</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord9 sord1" id="s98427">
					<div class="definition"><div name="s98427" class="pos-icon">adjective</div>
					 with or in a close or intimate relationship</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;a <strong>good</strong> friend&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/dear" class="word">dear</a>, 
				
					<a href="/dictionary/near" class="word">near</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/close" class="word">close</a>
					
					
						<div class="definition">close in relevance or relationship</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord10 sord1" id="s100154">
					<div class="definition"><div name="s100154" class="pos-icon">adjective</div>
					 generally admired</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;<strong>good</strong> taste&#8221;</div>
					
					
					


					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/discriminant" class="word">discriminant</a>, 
					
						<a href="/dictionary/discriminating" class="word">discriminating</a>
					
					
						<div class="definition">showing or indicating careful judgment and discernment especially in matters of taste</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord11 sord1" id="s101623">
					<div class="definition"><div name="s101623" class="pos-icon">adjective</div>
					 resulting favorably</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;it's a <strong>good</strong> thing that I wasn't there&#8221;</div>
					
						<div class="example">&#8220;it is <strong>good</strong> that you stayed&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/well" class="word">well</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/fortunate" class="word">fortunate</a>
					
					
						<div class="definition">having unexpected good fortune</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord12 sord1" id="s108461">
					<div class="definition"><div name="s108461" class="pos-icon">adjective</div>
					 financially sound</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;a <strong>good</strong> investment&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/dependable" class="word">dependable</a>, 
				
					<a href="/dictionary/safe" class="word">safe</a>, 
				
					<a href="/dictionary/secure" class="word">secure</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/sound" class="word">sound</a>
					
					
						<div class="definition">financially secure and safe</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord13 sord1" id="s101738">
					<div class="definition"><div name="s101738" class="pos-icon">adjective</div>
					 not left to spoil</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;the meat is still <strong>good</strong>&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/undecomposed" class="word">undecomposed</a>, 
				
					<a href="/dictionary/unspoiled" class="word">unspoiled</a>, 
				
					<a href="/dictionary/unspoilt" class="word">unspoilt</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/fresh" class="word">fresh</a>
					
					
						<div class="definition">recently made, produced, or harvested</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_n ord14 sord1" id="s28554">
					<div class="definition"><div name="s28554" class="pos-icon">noun</div>
					 benefit</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;for your own <strong>good</strong>&#8221;</div>
					
						<div class="example">&#8220;what's the <strong>good</strong> of worrying?&#8221;</div>
					
					
					


					
					


					
					
					
					
					
					
					
					
					
					
					
						<div class="more-info-section">
							<a class="more-info-expander" href="#0"><span class="expand-text">see more</span><span class="hide-text">see less</span><span class="carat-icon"></span></a>
							<div class="more-info">
								


								
								
								


								
								
									



	

	<div class="div-replace-dl instances">
		<span class="detail">types:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/common good" class="word">common good</a>, 
					
						<a href="/dictionary/commonweal" class="word">commonweal</a>, 
					
						<a href="/dictionary/weal" class="word">weal</a>
					
					
						<div class="definition">the good of a community</div>
					
				</div>			
			
		
		
	</div>			

								
								



	

	<div class="div-replace-dl instances">
		<span class="detail">type of:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/advantage" class="word">advantage</a>, 
					
						<a href="/dictionary/vantage" class="word">vantage</a>
					
					
						<div class="definition">the quality of having a superior or more favorable position</div>
					
				</div>			
			
		
		
	</div>			

								
								


								


							</div>
						</div>
					
				</div>
				</li>
				
				
				<li class="sense pos_n ord15 sord1" id="s26928">
					<div class="definition"><div name="s26928" class="pos-icon">noun</div>
					 moral excellence or admirableness</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;there is much <strong>good</strong> to be found in people&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/goodness" class="word">goodness</a>
				
			</span>
		
		
		
	</div>			

					


					
					
					
					
					
					
					
					
					
					
					
					
						<div class="more-info-section">
							<a class="more-info-expander" href="#0"><span class="expand-text">see more</span><span class="hide-text">see less</span><span class="carat-icon"></span></a>
							<div class="more-info">
								



	

	<div class="div-replace-dl instances">
		<span class="detail">antonyms:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/evil" class="word">evil</a>
					
					
						<div class="definition">the quality of being morally wrong in principle or practice</div>
					
				</div>			
			
		
		
	</div>			

								
								
								


								
								
									



	

	<div class="div-replace-dl instances">
		<span class="detail">types:</span>
		
			<div class="div-replace-dd more">
				<a href="javascript:void(0);" class="expander">show 13 types...</a>
			</div>
			<div class="div-replace-dd less">
				<a href="javascript:void(0);" class="expander">hide 13 types...</a>
			</div>
			
		
		
		
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/kindness" class="word">kindness</a>
					
					
						<div class="definition">the quality of being warmhearted and considerate and humane and sympathetic</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/beneficence" class="word">beneficence</a>
					
					
						<div class="definition">the quality of being kind or helpful or generous</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/benignancy" class="word">benignancy</a>, 
					
						<a href="/dictionary/benignity" class="word">benignity</a>, 
					
						<a href="/dictionary/graciousness" class="word">graciousness</a>
					
					
						<div class="definition">the quality of being kind and gentle</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/moral excellence" class="word">moral excellence</a>, 
					
						<a href="/dictionary/virtue" class="word">virtue</a>, 
					
						<a href="/dictionary/virtuousness" class="word">virtuousness</a>
					
					
						<div class="definition">the quality of doing what is right and avoiding what is wrong</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/virtue" class="word">virtue</a>
					
					
						<div class="definition">a particular moral excellence</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/saintliness" class="word">saintliness</a>
					
					
						<div class="definition">the quality of resembling a saint</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/summum bonum" class="word">summum bonum</a>
					
					
						<div class="definition">the supreme good in which all moral values are included or from which they are derived</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/generosity" class="word">generosity</a>, 
					
						<a href="/dictionary/generousness" class="word">generousness</a>
					
					
						<div class="definition">the trait of being willing to give your money or time</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/benevolence" class="word">benevolence</a>
					
					
						<div class="definition">an inclination to do kind or charitable acts</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/free grace" class="word">free grace</a>, 
					
						<a href="/dictionary/grace" class="word">grace</a>, 
					
						<a href="/dictionary/grace of God" class="word">grace of God</a>
					
					
						<div class="definition">(Christian theology) the free and unmerited favor or beneficence of God</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/loving-kindness" class="word">loving-kindness</a>
					
					
						<div class="definition">tender kindness motivated by a feeling of affection</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/considerateness" class="word">considerateness</a>, 
					
						<a href="/dictionary/consideration" class="word">consideration</a>, 
					
						<a href="/dictionary/thoughtfulness" class="word">thoughtfulness</a>
					
					
						<div class="definition">kind and considerate regard for others</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/cardinal virtue" class="word">cardinal virtue</a>
					
					
						<div class="definition">one of the seven preeminent virtues</div>
					
				</div>			
			
		
		
	</div>			

								
								



	

	<div class="div-replace-dl instances">
		<span class="detail">type of:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/morality" class="word">morality</a>
					
					
						<div class="definition">concern with the distinction between good and evil or right and wrong; right or good conduct</div>
					
				</div>			
			
		
		
	</div>			

								
								


								


							</div>
						</div>
					
				</div>
				</li>
				
				
				<li class="sense pos_n ord16 sord1" id="s28466">
					<div class="definition"><div name="s28466" class="pos-icon">noun</div>
					 that which is pleasing or valuable or useful</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;weigh the <strong>good</strong> against the bad&#8221;</div>
					
						<div class="example">&#8220;among the highest <strong>goods</strong> of all are happiness and self-realization&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/goodness" class="word">goodness</a>
				
			</span>
		
		
		
	</div>			

					


					
					
					
					
					
					
					
					
					
					
					
					
						<div class="more-info-section">
							<a class="more-info-expander" href="#0"><span class="expand-text">see more</span><span class="hide-text">see less</span><span class="carat-icon"></span></a>
							<div class="more-info">
								



	

	<div class="div-replace-dl instances">
		<span class="detail">antonyms:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/bad" class="word">bad</a>
					
					
						<div class="definition">that which is below standard or expectations as of ethics or decency</div>
					
				</div>			
			
		
		
	</div>			

								
								
								


								
								
									



	

	<div class="div-replace-dl instances">
		<span class="detail">types:</span>
		
			<div class="div-replace-dd more">
				<a href="javascript:void(0);" class="expander">show 15 types...</a>
			</div>
			<div class="div-replace-dd less">
				<a href="javascript:void(0);" class="expander">hide 15 types...</a>
			</div>
			
		
		
		
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/worthiness" class="word">worthiness</a>
					
					
						<div class="definition">the quality or state of having merit or value</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/desirability" class="word">desirability</a>, 
					
						<a href="/dictionary/desirableness" class="word">desirableness</a>
					
					
						<div class="definition">the quality of being worthy of desiring</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/benefit" class="word">benefit</a>, 
					
						<a href="/dictionary/welfare" class="word">welfare</a>
					
					
						<div class="definition">something that aids or promotes well-being</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/better" class="word">better</a>
					
					
						<div class="definition">something superior in quality or condition or effect</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/better" class="word">better</a>
					
					
						<div class="definition">the superior one of two alternatives</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/optimum" class="word">optimum</a>
					
					
						<div class="definition">most favorable conditions or greatest degree or amount possible under given circumstances</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/soundness" class="word">soundness</a>, 
					
						<a href="/dictionary/wisdom" class="word">wisdom</a>, 
					
						<a href="/dictionary/wiseness" class="word">wiseness</a>
					
					
						<div class="definition">the quality of being prudent and sensible</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/deservingness" class="word">deservingness</a>, 
					
						<a href="/dictionary/merit" class="word">merit</a>, 
					
						<a href="/dictionary/meritoriousness" class="word">meritoriousness</a>
					
					
						<div class="definition">the quality of being deserving (e.g., deserving assistance)</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/laudability" class="word">laudability</a>, 
					
						<a href="/dictionary/laudableness" class="word">laudableness</a>, 
					
						<a href="/dictionary/praiseworthiness" class="word">praiseworthiness</a>
					
					
						<div class="definition">the quality of being worthy of praise</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/quotability" class="word">quotability</a>
					
					
						<div class="definition">the quality of being worthy of being quoted</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/roadworthiness" class="word">roadworthiness</a>
					
					
						<div class="definition">(of motor vehicles) the quality of being fit to drive on the open road</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/advantage" class="word">advantage</a>, 
					
						<a href="/dictionary/reward" class="word">reward</a>
					
					
						<div class="definition">benefit resulting from some event or action</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/interest" class="word">interest</a>, 
					
						<a href="/dictionary/sake" class="word">sake</a>
					
					
						<div class="definition">a reason for wanting something done</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/advisability" class="word">advisability</a>
					
					
						<div class="definition">the quality of being advisable</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/reasonableness" class="word">reasonableness</a>
					
					
						<div class="definition">goodness of reason and judgment</div>
					
				</div>			
			
		
		
	</div>			

								
								



	

	<div class="div-replace-dl instances">
		<span class="detail">type of:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/quality" class="word">quality</a>
					
					
						<div class="definition">an essential and distinguishing attribute of something or someone</div>
					
				</div>			
			
		
		
	</div>			

								
								


								


							</div>
						</div>
					
				</div>
				</li>
				
				
				<li class="sense pos_r ord17 sord1" id="s114093">
					<div class="definition"><div name="s114093" class="pos-icon">adverb</div>
					 (often used as a combining form) in a good or proper or satisfactory manner or to a high standard (`good&#039; is a nonstandard dialectal variant for `well&#039;)</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;the baby can walk pretty <strong>good</strong>&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/well" class="word">well</a>
				
			</span>
		
		
		
	</div>			

					


					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord1 sord1" id="s96443">
					<div class="definition"><div name="s96443" class="pos-icon">adjective</div>
					 having the normally expected amount</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;gives <strong>good</strong> measure&#8221;</div>
					
						<div class="example">&#8220;a <strong>good</strong> mile from here&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/full" class="word">full</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/ample" class="word">ample</a>
					
					
						<div class="definition">more than enough in size or scope or capacity</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord2 sord1" id="s98818">
					<div class="definition"><div name="s98818" class="pos-icon">adjective</div>
					 thorough</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;had a <strong>good</strong> workout&#8221;</div>
					
						<div class="example">&#8220;gave the house a <strong>good</strong> cleaning&#8221;</div>
					
					
					


					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/complete" class="word">complete</a>
					
					
						<div class="definition">having every necessary or normal part or component or step</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_r ord3 sord1" id="s114363">
					<div class="definition"><div name="s114363" class="pos-icon">adverb</div>
					 completely and absolutely (`good&#039; is sometimes used informally for `thoroughly&#039;)</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;we beat him <strong>good</strong>&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/soundly" class="word">soundly</a>, 
				
					<a href="/dictionary/thoroughly" class="word">thoroughly</a>
				
			</span>
		
		
		
	</div>			

					


					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord1 sord1" id="s100459">
					<div class="definition"><div name="s100459" class="pos-icon">adjective</div>
					 exerting force or influence</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;a warranty <strong>good</strong> for two years&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/effective" class="word">effective</a>, 
				
					<a href="/dictionary/in effect" class="word">in effect</a>, 
				
					<a href="/dictionary/in force" class="word">in force</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/operative" class="word">operative</a>
					
					
						<div class="definition">being in force or having or exerting force</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_a ord2 sord1" id="s102004">
					<div class="definition"><div name="s102004" class="pos-icon">adjective</div>
					 not forged</div>
					<div class="defContent">
					
					
						<div class="example">&#8220;a <strong>good</strong> dollar bill&#8221;</div>
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/honest" class="word">honest</a>
				
			</span>
		
		
		
	</div>			

					



	

	<div class="div-replace-dl instances">
		<span class="detail"></span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/echt" class="word">echt</a>, 
					
						<a href="/dictionary/genuine" class="word">genuine</a>
					
					
						<div class="definition">not fake or counterfeit</div>
					
				</div>			
			
		
		
	</div>			

					
					
					
					
					
					
					
					
					
					
					
					
				</div>
				</li>
				
				
				<li class="sense pos_n ord1 sord1" id="s16662">
					<div class="definition"><div name="s16662" class="pos-icon">noun</div>
					 articles of commerce</div>
					<div class="defContent">
					
					
					
					



	

	<div class="div-replace-dl instances">
		<span class="detail">synonyms:</span>
		
		
			<span>
				
					<a href="/dictionary/commodity" class="word">commodity</a>, 
				
					<a href="/dictionary/trade good" class="word">trade good</a>
				
			</span>
		
		
		
	</div>			

					


					
					
					
					
					
					
					
					
					
					
					
					
						<div class="more-info-section">
							<a class="more-info-expander" href="#0"><span class="expand-text">see more</span><span class="hide-text">see less</span><span class="carat-icon"></span></a>
							<div class="more-info">
								


								
								
								


								
								
									



	

	<div class="div-replace-dl instances">
		<span class="detail">types:</span>
		
			<div class="div-replace-dd more">
				<a href="javascript:void(0);" class="expander">show 39 types...</a>
			</div>
			<div class="div-replace-dd less">
				<a href="javascript:void(0);" class="expander">hide 39 types...</a>
			</div>
			
		
		
		
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/basic" class="word">basic</a>, 
					
						<a href="/dictionary/staple" class="word">staple</a>
					
					
						<div class="definition">(usually plural) a necessary commodity for which demand is constant</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/consumer goods" class="word">consumer goods</a>
					
					
						<div class="definition">goods (as food or clothing) intended for direct use or consumption</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/drygoods" class="word">drygoods</a>, 
					
						<a href="/dictionary/soft goods" class="word">soft goods</a>
					
					
						<div class="definition">textiles or clothing and related merchandise</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/entrant" class="word">entrant</a>
					
					
						<div class="definition">a commodity that enters competition with established merchandise</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/export" class="word">export</a>, 
					
						<a href="/dictionary/exportation" class="word">exportation</a>
					
					
						<div class="definition">commodities (goods or services) sold to a foreign country</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/fancy goods" class="word">fancy goods</a>
					
					
						<div class="definition">goods that are chiefly ornamental</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/fungible" class="word">fungible</a>
					
					
						<div class="definition">a commodity that is freely interchangeable with another in satisfying an obligation</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/future" class="word">future</a>
					
					
						<div class="definition">bulk commodities bought or sold at an agreed price for delivery at a specified future date</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/import" class="word">import</a>, 
					
						<a href="/dictionary/importation" class="word">importation</a>
					
					
						<div class="definition">commodities (goods or services) bought from a foreign country</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/merchandise" class="word">merchandise</a>, 
					
						<a href="/dictionary/product" class="word">product</a>, 
					
						<a href="/dictionary/ware" class="word">ware</a>
					
					
						<div class="definition">commodities offered for sale</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/middling" class="word">middling</a>
					
					
						<div class="definition">any commodity of intermediate quality or size (especially when coarse particles of ground wheat are mixed with bran)</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/shopping" class="word">shopping</a>
					
					
						<div class="definition">the commodities purchased from stores</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/sporting goods" class="word">sporting goods</a>
					
					
						<div class="definition">sports equipment sold as a commodity</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/worldly good" class="word">worldly good</a>, 
					
						<a href="/dictionary/worldly possession" class="word">worldly possession</a>
					
					
						<div class="definition">a commodity or good associated with the earthly, rather than the spiritual, existence of human beings</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/salvage" class="word">salvage</a>
					
					
						<div class="definition">property or goods saved from damage or destruction</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/cargo" class="word">cargo</a>, 
					
						<a href="/dictionary/consignment" class="word">consignment</a>, 
					
						<a href="/dictionary/freight" class="word">freight</a>, 
					
						<a href="/dictionary/lading" class="word">lading</a>, 
					
						<a href="/dictionary/load" class="word">load</a>, 
					
						<a href="/dictionary/loading" class="word">loading</a>, 
					
						<a href="/dictionary/payload" class="word">payload</a>, 
					
						<a href="/dictionary/shipment" class="word">shipment</a>
					
					
						<div class="definition">goods carried by a large vehicle</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/article of clothing" class="word">article of clothing</a>, 
					
						<a href="/dictionary/clothing" class="word">clothing</a>, 
					
						<a href="/dictionary/habiliment" class="word">habiliment</a>, 
					
						<a href="/dictionary/vesture" class="word">vesture</a>, 
					
						<a href="/dictionary/wear" class="word">wear</a>, 
					
						<a href="/dictionary/wearable" class="word">wearable</a>
					
					
						<div class="definition">a covering designed to be worn on a person's body</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/contraband" class="word">contraband</a>
					
					
						<div class="definition">goods whose importation or exportation or possession is prohibited by law</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/consumer durables" class="word">consumer durables</a>, 
					
						<a href="/dictionary/durable goods" class="word">durable goods</a>, 
					
						<a href="/dictionary/durables" class="word">durables</a>
					
					
						<div class="definition">consumer goods that are not destroyed by use</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/fashion" class="word">fashion</a>
					
					
						<div class="definition">consumer goods (especially clothing) in the current mode</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/feature" class="word">feature</a>
					
					
						<div class="definition">an article of merchandise that is displayed or advertised more than other articles</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/generic" class="word">generic</a>
					
					
						<div class="definition">any product that can be sold without a brand name</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/foodstuff" class="word">foodstuff</a>, 
					
						<a href="/dictionary/grocery" class="word">grocery</a>
					
					
						<div class="definition">(usually plural) consumer goods sold by a grocer</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/haberdashery" class="word">haberdashery</a>, 
					
						<a href="/dictionary/men's furnishings" class="word">men's furnishings</a>
					
					
						<div class="definition">the drygoods sold by a haberdasher</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/ironmongery" class="word">ironmongery</a>
					
					
						<div class="definition">the merchandise that is sold in an ironmonger's shop</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/irregular" class="word">irregular</a>, 
					
						<a href="/dictionary/second" class="word">second</a>
					
					
						<div class="definition">merchandise that has imperfections; usually sold at a reduced price without the brand name</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/business line" class="word">business line</a>, 
					
						<a href="/dictionary/line" class="word">line</a>, 
					
						<a href="/dictionary/line of business" class="word">line of business</a>, 
					
						<a href="/dictionary/line of merchandise" class="word">line of merchandise</a>, 
					
						<a href="/dictionary/line of products" class="word">line of products</a>, 
					
						<a href="/dictionary/product line" class="word">product line</a>
					
					
						<div class="definition">a particular kind of product or merchandise</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/number" class="word">number</a>
					
					
						<div class="definition">an item of merchandise offered for sale</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/oil future" class="word">oil future</a>, 
					
						<a href="/dictionary/petroleum future" class="word">petroleum future</a>
					
					
						<div class="definition">petroleum bought or sold at an agreed price for delivery at a specified future date</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/refill" class="word">refill</a>
					
					
						<div class="definition">a commercial product that refills a container with its appropriate contents</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/release" class="word">release</a>
					
					
						<div class="definition">merchandise issued for sale or public showing (especially a record or film)</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/dreck" class="word">dreck</a>, 
					
						<a href="/dictionary/schlock" class="word">schlock</a>, 
					
						<a href="/dictionary/shlock" class="word">shlock</a>
					
					
						<div class="definition">merchandise that is shoddy or inferior</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/software package" class="word">software package</a>, 
					
						<a href="/dictionary/software product" class="word">software product</a>
					
					
						<div class="definition">merchandise consisting of a computer program that is offered for sale</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/soybean future" class="word">soybean future</a>
					
					
						<div class="definition">soybeans bought or sold at an agreed price for delivery at a specified future date</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/inventory" class="word">inventory</a>, 
					
						<a href="/dictionary/stock" class="word">stock</a>
					
					
						<div class="definition">the merchandise that a shop has on hand</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/top of the line" class="word">top of the line</a>
					
					
						<div class="definition">the best (most expensive) in a given line of merchandise</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/wheat future" class="word">wheat future</a>
					
					
						<div class="definition">wheat bought or sold at an agreed price for delivery at a specified future date</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/household linen" class="word">household linen</a>, 
					
						<a href="/dictionary/white goods" class="word">white goods</a>
					
					
						<div class="definition">drygoods for household use that are typically made of white cloth</div>
					
				</div>			
			
				
				<div class="div-replace-dd less">
					
						<a href="/dictionary/piece goods" class="word">piece goods</a>, 
					
						<a href="/dictionary/yard goods" class="word">yard goods</a>
					
					
						<div class="definition">merchandise in the form of fabrics sold by the yard</div>
					
				</div>			
			
		
		
	</div>			

								
								



	

	<div class="div-replace-dl instances">
		<span class="detail">type of:</span>
		
		
		
			
				
				<div class="div-replace-dd ">
					
						<a href="/dictionary/artefact" class="word">artefact</a>, 
					
						<a href="/dictionary/artifact" class="word">artifact</a>
					
					
						<div class="definition">a man-made object taken as a whole</div>
					
				</div>			
			
		
		
	</div>			

								
								


								


							</div>
						</div>
					
				</div>
				</li>
				
			</ol>
				
			</div>
			
			
				<script type="text/javascript">
				Module.after(['jquery'], function(){
					jQuery(function($){
						$('.pron-video').parent().click(function(){
							$(this).children(".pron-video").get(0).play();
							$(this).children(".button-overlay").hide();
						});
						$('.pron-video').on('ended', function(){
							$(this).parent().children(".button-overlay").show();
						})
					});
				});
				</script>
				<div class="word-definitions" style="padding-bottom: 16px;">
					<div class="label">Pronunciation</div>
					<div class="videos">
					
					
					
					<div class="video-with-label">
						<div class="video-label">
							<div class="us-flag-icon"></div>
							<div class="region-label">US</div>
						</div>
						<div class="wrapper">
						<div class="button-overlay"></div>
						<video class="pron-video" poster="https://sd-pronunciation-processed-videos.sdcdns.com/speakers-2/desktop_5@1x.jpg" playsinline>
							<source src="https://sd-pronunciation-processed-videos.sdcdns.com/desktop/lang_en_pron_44_speaker_5_syllable_all_version_51.mp4" type="video/mp4">			
						</video>
						</div>
						<span class="span-replace-h3">/gʊd/</span>
					</div>
					
					
					
					
					
					<div class="video-with-label">
						<div class="video-label">
							<div class="uk-flag-icon"></div>
							<div class="region-label">UK</div>
						</div>
						<div class="wrapper">
						<div class="button-overlay"></div>
						<video class="pron-video" poster="https://sd-pronunciation-processed-videos.sdcdns.com/speakers-2/desktop_8@1x.jpg" playsinline>
							<source src="https://sd-pronunciation-processed-videos.sdcdns.com/desktop/lang_en_pron_4348_speaker_8_syllable_all_version_50.mp4" type="video/mp4">			
						</video>
						</div>
						<span class="span-replace-h3">/gʊd/</span>
					</div>
					
					
					</div>
				</div>
			
			<div class="section citation">
					<div class="header-text">Cite this entry</div> 
					<div class="style-wrapper"> 
						<div class="style">Style:</div>
						<div class="style-dropdown-wrapper">
							<div class="style-dropdown-component">
								<div class="style-dropdown-select">MLA</div>
								<ul class="style-dropdown-choices">
									<li>MLA</li>
									<li>APA</li>
									<li>Chicago</li>
								</ul>
							</div>
						</div>
					</div> 
					<div class="citation-wrapper" data-word="good" data-mdy="July 12, 2026" data-dmy-mla="12 July 2026">
						<p id="citation-area"></p>
						<button class="citation-copy" type="button">Copy citation</button>
						<div id="copyArea" contenteditable="true"></div>
					</div>
				</div>
		</div>
		<div class="col-2">
			<div class="box-market-bowl-subscription"></div>
			
			<div class="section examples">
				<vcom:examples word="good" count="4" title="Examples from books and articles"></vcom:examples>
				<div class="disclaimer">DISCLAIMER: These example sentences appear in various news sources and books to reflect the usage of the word <b>‘good'</b>. 
				Views expressed in the examples do not represent the opinion of <a href="/">Vocabulary.com</a> or its editors. 
				<a href="https://www.ixl.com/feedback/vocabularydotcom">Send us feedback</a></div>
			</div>	
			
			
				<div class="word-definitions ccw">
					<div class="label">Commonly confused words</div>
						<div class="word-area">
							<h4><a href="/articles/tasty-morsels/a-personality-test-what-does-good-say-about-you/">A Personality Test: What Does "Good" Say About You?</a></h4>
							<div class="body">
								Find out where the word "good" leads you in this tongue-in-cheek personality quiz flowchart from Vocabulary.com.
								<p><a class="readMore" href="/articles/tasty-morsels/a-personality-test-what-does-good-say-about-you/">Continue reading...</a></p>
						</div>
					</div>
				</div>
			
			
			<div class="section family"><div class="header-text">Word Family</div> 
				<vcom:wordfamily lang="en" word="good" data="[{&#034;word&#034;:&#034;good&#034;,&#034;hw&#034;:true,&#034;freq&#034;:678.0652573232803,&#034;ffreq&#034;:1248.7570793861516,&#034;type&#034;:0},{&#034;word&#034;:&#034;better&#034;,&#034;hw&#034;:true,&#034;parent&#034;:&#034;good&#034;,&#034;freq&#034;:292.2596813498864,&#034;ffreq&#034;:295.12414617808986,&#034;type&#034;:1},{&#034;word&#034;:&#034;best&#034;,&#034;hw&#034;:true,&#034;parent&#034;:&#034;good&#034;,&#034;freq&#034;:221.72460395984248,&#034;ffreq&#034;:222.19400527325433,&#034;type&#034;:1},{&#034;word&#034;:&#034;goods&#034;,&#034;parent&#034;:&#034;good&#034;,&#034;freq&#034;:34.20639390900686,&#034;ffreq&#034;:34.20639390900686,&#034;type&#034;:1},{&#034;word&#034;:&#034;goodness&#034;,&#034;hw&#034;:true,&#034;parent&#034;:&#034;good&#034;,&#034;freq&#034;:18.929360968325,&#034;ffreq&#034;:18.948651433259734,&#034;type&#034;:2},{&#034;word&#034;:&#034;betters&#034;,&#034;parent&#034;:&#034;better&#034;,&#034;freq&#034;:1.0785738902982456,&#034;ffreq&#034;:1.0785738902982456,&#034;type&#034;:1},{&#034;word&#034;:&#034;betterment&#034;,&#034;hw&#034;:true,&#034;parent&#034;:&#034;better&#034;,&#034;freq&#034;:0.7198389283540535,&#034;ffreq&#034;:0.7553739953390913,&#034;type&#034;:3},{&#034;word&#034;:&#034;bettered&#034;,&#034;parent&#034;:&#034;better&#034;,&#034;freq&#034;:0.5844672446015281,&#034;ffreq&#034;:0.5844672446015281,&#034;type&#034;:1},{&#034;word&#034;:&#034;bettering&#034;,&#034;hw&#034;:true,&#034;parent&#034;:&#034;better&#034;,&#034;freq&#034;:0.4358968216831316,&#034;ffreq&#034;:0.4358968216831316,&#034;type&#034;:1},{&#034;word&#034;:&#034;bested&#034;,&#034;parent&#034;:&#034;best&#034;,&#034;freq&#034;:0.253821907035985,&#034;ffreq&#034;:0.253821907035985,&#034;type&#034;:1},{&#034;word&#034;:&#034;goodish&#034;,&#034;hw&#034;:true,&#034;parent&#034;:&#034;good&#034;,&#034;freq&#034;:0.1753063304595203,&#034;ffreq&#034;:0.1753063304595203,&#034;type&#034;:2},{&#034;word&#034;:&#034;besting&#034;,&#034;parent&#034;:&#034;best&#034;,&#034;freq&#034;:0.06971641713255054,&#034;ffreq&#034;:0.06971641713255054,&#034;type&#034;:1},{&#034;word&#034;:&#034;bester&#034;,&#034;parent&#034;:&#034;best&#034;,&#034;freq&#034;:0.04196522196328285,&#034;ffreq&#034;:0.04196522196328285,&#034;type&#034;:1},{&#034;word&#034;:&#034;bests&#034;,&#034;parent&#034;:&#034;best&#034;,&#034;freq&#034;:0.040273075916376286,&#034;ffreq&#034;:0.040273075916376286,&#034;type&#034;:1},{&#034;word&#034;:&#034;betterments&#034;,&#034;parent&#034;:&#034;betterment&#034;,&#034;freq&#034;:0.035535066985037896,&#034;ffreq&#034;:0.035535066985037896,&#034;type&#034;:1},{&#034;word&#034;:&#034;goodnesses&#034;,&#034;parent&#034;:&#034;goodness&#034;,&#034;freq&#034;:0.01929046493473486,&#034;ffreq&#034;:0.01929046493473486,&#034;type&#034;:1},{&#034;word&#034;:&#034;betterly&#034;,&#034;parent&#034;:&#034;better&#034;,&#034;freq&#034;:6.768584187626267E-4,&#034;ffreq&#034;:6.768584187626267E-4,&#034;type&#034;:1}]"></vcom:wordfamily>
			</div>
			<div class="section related-lists">
				










<link href="https://cdn.vocabulary.com/css/related-lists-17m06op.css" rel="stylesheet" type="text/css"/>


            
            
            
            
            
            
            


    <h3 class="hdr-vocab-list">
        Vocabulary lists containing <strong>good</strong>
    </h3>
    
    	
    	
    	
    	
        
        
        
       	
       	
        
            
            
                <div class="box-vocab-item">
                	
                		
                    	
                	
                    <div class="vocab-list-content">
                        <a
                          class="vlist-title"
                          href="/lists/1573079"
                        >Economics</a>
                        <p class="vlist-txt">
                            If you have an appreciation for finance, budget some time to review this list of terms related to economics. You'll learn all about capitalism, markets, and stocks and bonds. Once you've mastered these words, your vocabulary will be one of your greatest assets.
                        </p>
                    </div>
                </div>
            
        
    
    	
    	
    	
    	
        
        
        
       	
       	
       		
       			
       			
       			
       				
       			
       		
		
        
            
            
                <div class="box-vocab-item">
                	
                		
                    	
                	
                    <div class="vocab-list-content">
                        <a
                          class="vlist-title"
                          href="/lists/8090214"
                        >One Idea, Part 1</a>
                        <p class="vlist-txt">
                            
                        </p>
                    </div>
                </div>
            
        
    
    <div class="box-more-vocab">
 		<a class="lk-more-vocab" href="/lists/">MORE VOCABULARY LISTS</a>
	</div>


			</div>
		</div>
		</div>
	    <div class="sticky-banner" style="display: none">
		 	<div class="banner">
		 		<span class="note">2 million people are mastering new words.</span>
		 		<a role="button" class="master-word-button" href="/vocabtrainer/"><span>Master a word</span></a>
		 	
		 	</div>
		 	<div class="side-icon-background">
			 	<svg xmlns="http://www.w3.org/2000/svg" width="112" height="105" viewBox="0 0 112 105" fill="none">
				  <circle cx="100" cy="100" r="100" fill="#00578A"/>
				</svg>
			</div>
			<div class="side-icon">
				<svg xmlns="http://www.w3.org/2000/svg" width="138" height="97" viewBox="0 0 138 97" fill="none">
				  <path d="M46.2126 19.3856C41.0786 28.6768 42.552 39.7123 49.5035 44.034L54.3084 47.2077L72.9 13.5609L68.0951 10.3873C61.1437 6.06559 51.3465 10.0943 46.2126 19.3856Z" fill="#008ECB"/>
				  <ellipse cx="15.0748" cy="19.1922" rx="15.0748" ry="19.1922" transform="matrix(0.840519 0.521584 -0.487581 0.880794 60.8337 6.01709)" fill="#00C1FF"/>
				  <path d="M70.2748 59.6028C69.2218 65.1896 83.7232 69.8013 86.0971 64.1418C86.0971 64.1418 85.8095 61.6132 79.3292 59.4784C72.8489 57.3436 70.2748 59.6028 70.2748 59.6028Z" fill="#338300"/>
				  <path fill-rule="evenodd" clip-rule="evenodd" d="M31.076 115.202C53.8683 95.2145 64.2363 85.0047 73.4583 57.7732L85.7781 61.4364C75.827 90.8207 72.3644 100.416 47.4444 131.068L31.076 115.202Z" fill="#D36D59"/>
				  <path d="M66.919 73.5376C69.0306 68.925 69.5397 67.3249 71.4115 62.0317L83.9718 66.6871C81.6791 73.1705 82.6792 72.2929 80.0966 77.7181C76.02 78.9947 69.7916 77.4068 66.919 73.5376Z" fill="#BB5541"/>
				  <path d="M74.902 62.873C78.9844 64.6815 88.1901 64.7603 93.1474 57.1513C98.1047 49.5424 104.177 41.285 97.5399 40.3943C98.5068 37.632 94.8381 34.0181 91.8137 37.8566C94.1718 34.6838 90.2413 30.2216 86.0336 35.7514C87.6914 32.8144 84.149 30.1739 81.1 33.2909C78.675 35.6372 76.91 39.6455 76.91 39.6455C76.91 39.6455 74.6485 38.6855 70.7082 42.414C66.7679 46.1426 64.4933 58.2559 74.8912 62.8672L74.902 62.873Z" fill="#D36D59"/>
				  <path d="M95.2184 53.809C92.3763 60.6926 88.3086 59.6106 79.8536 56.1069C71.3986 52.6033 71.3646 44.8962 83.04 47.483C87.2898 48.4246 96.8963 49.0785 95.2184 53.809Z" fill="#BB5541"/>
				  <path d="M70.5172 25.205C68.0823 23.9666 65.0784 26.1847 62.6945 29.7558C60.2941 33.3104 60.3087 37.2217 62.7273 38.4436L95.6187 56.3209C98.0536 57.5593 101.953 55.6891 104.337 52.118C106.738 48.5634 106.723 44.6521 104.304 43.4302L70.5172 25.205Z" fill="#0368A2"/>
				  <path d="M77.6565 38.64C76.1444 37.8294 75.7195 35.86 76.7111 34.2589L80.5715 28.0262C81.5632 26.425 83.6078 25.7795 85.1199 26.5901C86.6321 27.4007 87.057 29.3701 86.0653 30.9712L82.2049 37.204C81.2133 38.8051 79.1686 39.4506 77.6565 38.64Z" fill="#D36D59"/>
				  <path d="M82.9168 41.0847C81.4061 40.2747 80.9962 38.2829 82.0049 36.6539L85.9313 30.3125C86.94 28.6835 88.9973 28.0147 90.508 28.8247C92.0187 29.6347 92.4286 31.6265 91.4199 33.2555L87.4935 39.5969C86.4848 41.2259 84.4275 41.8947 82.9168 41.0847Z" fill="#D36D59"/>
				  <path d="M88.629 44.4174C87.1238 43.6096 86.7746 41.527 87.8521 39.7846L92.0465 33.0018C93.124 31.2594 95.233 30.4963 96.7381 31.3041C98.2432 32.112 98.5924 34.1946 97.5149 35.937L93.3205 42.7198C92.243 44.4622 90.1341 45.2253 88.629 44.4174Z" fill="#D36D59"/>
				  <path d="M94.1033 47.5824C92.5792 46.7669 92.0365 44.9704 92.896 43.586L96.2418 38.1969C97.1013 36.8125 99.0478 36.348 100.572 37.1635C102.096 37.979 102.639 39.7755 101.779 41.1599L98.4333 46.5489C97.5738 47.9333 95.6274 48.3979 94.1033 47.5824Z" fill="#D36D59"/>
				  <path d="M86.3221 43.3789C79.7059 40.4608 77.1483 39.11 74.7091 38.8806C68.2309 39.5927 67.5142 44.886 67.1249 47.3752C66.5198 51.2085 67.3828 55.9497 71.0762 59.5334C75.4506 62.3835 79.9748 59.375 80.6805 56.0703C81.3862 52.7656 78.2699 49.1706 77.2744 47.9839C84.5377 52.056 90.515 45.4304 86.3277 43.3821L86.3221 43.3789Z" fill="#D36D59"/>
				  <path d="M70.4466 59.5363C70.7529 62.8369 85.3064 66.0655 86.1599 64.0348L82.228 76.0623C77.2106 78.4232 67.7944 74.2675 66.0338 71.306L70.4466 59.5363Z" fill="#44AA02"/>
				  <path d="M96.1943 46.5254C91.0603 55.8167 92.5337 66.8522 99.4852 71.1739L104.29 74.3476L122.882 40.7008L118.077 37.5271C111.125 33.2055 101.328 37.2342 96.1943 46.5254Z" fill="#008ECB"/>
				  <ellipse cx="15.0748" cy="19.1922" rx="15.0748" ry="19.1922" transform="matrix(0.840519 0.521584 -0.487581 0.880794 110.815 33.1568)" fill="#00C1FF"/>
				  <path d="M110.225 55.8159C108.677 58.0264 109.728 60.8101 110.59 61.5136L113.513 63.3394L118.052 55.1367L115.745 53.5665C114.668 52.7579 111.774 53.6054 110.225 55.8159Z" fill="#008ECB"/>
				  <ellipse cx="3.66271" cy="4.66361" rx="3.66271" ry="4.66361" transform="matrix(0.840523 0.52157 -0.487591 0.880785 115.123 53.3307)" fill="#0368A1"/>
				</svg>
			</div> 
			<div class="close-button">
				<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
					<path fill-rule="evenodd" clip-rule="evenodd" d="M2.27736 15.4764C1.75666 15.9971 0.912443 15.9971 0.391744 15.4764C-0.128955 14.9557 -0.128953 14.1115 0.391746 13.5908L6.0486 7.93397L0.391746 2.27712C-0.128953 1.75642 -0.128955 0.9122 0.391744 0.391501C0.912443 -0.129198 1.75666 -0.129198 2.27736 0.391501L7.93422 6.04836L13.5911 0.391501C14.1118 -0.129198 14.956 -0.129198 15.4767 0.391501C15.9974 0.9122 15.9974 1.75642 15.4767 2.27712L9.81983 7.93397L15.4767 13.5908C15.9974 14.1115 15.9974 14.9557 15.4767 15.4764C14.956 15.9971 14.1118 15.9971 13.5911 15.4764L7.93422 9.81959L2.27736 15.4764Z" fill="#9B9B9B"/>
				</svg>
			</div>
	        
    	</div>
	</div>

	

	

<!-- CSS are specificied in main.css -->
<div class="sign-up-area">
	<h2 class="sign-up">Sign up now (it’s free!)</h2>
	<h3>Whether you’re a teacher or a learner, Vocabulary.com can put you or your class on the path to systematic vocabulary improvement.</h3>
	<a role="button" href="/signup/" class="signup-button">Get started</a>
</div>		
</div>
</div>
<script>
Module.after(['vcom/dictionary/citation'], function(){
	modules.vcom.dictionary.citation();
});
</script>
<script>
	Module.after(['jquery', 'vcom/api'], function(){
		if (!VCOM || !VCOM.auth) {
			console.error('VCOM.auth is missing. Failed to init sticky banner.');
			return;
		}
		VCOM.auth(function(auth) {
			if (!auth.paid) {
				const $adBanner = $('.sticky-banner'),
					$window = $(window);
				
			    function showAdOrNot() {
			        if ($window.width() <= 430 && !localStorage.getItem("vocabTrainerAdBannerClosed")) {
			        	$adBanner.show();
			        } else {
			        	$adBanner.hide();
			        }
			    }
			    showAdOrNot();
			    
			    $window.on('resize', function() {
			        showAdOrNot();
			    });
			    
			    $adBanner.on('click', '.close-button', function(){
		        	 $adBanner.hide();
		        	 localStorage.setItem("vocabTrainerAdBannerClosed", true);
		        });
			}
		}); 
	});
</script>
<script type="text/javascript">
	Module.after(['jquery'], function(){
		jQuery(function($){
			$('body').on('click','.wordPage a.expander',function(){
				 $(this).closest('.div-replace-dl').toggleClass('expanded');		
			}).on('click', '.wordPage a.more-info-expander', function() {
				$(this).closest('.more-info-section').toggleClass('show-more');
			});
		});
	});
</script>
<script>
	Module.after([
		'jquery',
		'vcom/api',
		'vcom/util',
		'vcom/marketing-bowl-subscription'
	], function() {

		jQuery(function($){

			const util = modules.vcom.util();

			const {
				AD_PURPOSE,
				AD_USER_TYPE,
				initAdsBowlSubscription,
			} = modules.vcom['marketing-bowl-subscription']();
	
			const $boxAdsBowlSubscription = $('.box-market-bowl-subscription');
			const $boxCol2 = $('.col-2');

			const searchedWord = "good";
			const isLearnable = Boolean('false' === 'true');
			const hasSenseWithImage = Boolean('false' === 'true');

			if (
				typeof util.isBowlActive !== 'function' ||
				typeof util.isBowlEnrollment !== 'function' ||
				typeof util.isEducators !== 'function' ||
				typeof util.isLearners !== 'function' ||
				typeof initAdsBowlSubscription !== 'function' ||
				$boxAdsBowlSubscription.length === 0 ||
				$boxCol2.length === 0 ||
				AD_PURPOSE === undefined ||
				AD_USER_TYPE === undefined
			) {
				console.warn('Parameters are missing. Failed to initAdsProgressPreviewQuiz.');
				return;
			}

			function initAdsProgressPreviewQuiz(auth) {

				if (auth === undefined || auth === null) {
					return;
				}

				if (auth.validUser && isLearnable) {
					const $progress = $('<vcom:progress></vcom:progress>');
					$progress.attr('word', searchedWord);
					$boxCol2.prepend($progress);
				}

				let userType = AD_USER_TYPE.ANONYMOUS;
				if (util.isLearners(auth)) {
					userType = AD_USER_TYPE.LEARNER;
				}
				if (util.isEducators(auth)) {
					userType = AD_USER_TYPE.EDUCATOR;
				}

				if (auth.validUser === false || auth.paid === false) {

					let adPurpose = AD_PURPOSE.DICTIONARY_SUBSCRIPTION;
					let jQPreview = null;

					if (userType === AD_USER_TYPE.ANONYMOUS && isLearnable) {
						adPurpose = AD_PURPOSE.DICTIONARY_SUBSCRIPTION_ANONYMOUS_LEARNABLE;
						jQPreview = $('<vcom:qpreview></vcom:qpreview>')
							.data('delay', 0)
							.data('isHideLabel', true)
							.data('learnable', isLearnable)
							.data('slide', true)
							.data('types', hasSenseWithImage ? 'I,S,P,F,D' : 'S,P,F,D')
							.data('word', searchedWord);
					}

					initAdsBowlSubscription({
						adPurpose,
						cssClassname: '',
						jContainer: $boxAdsBowlSubscription,
						jQPreview,
						targetWord: searchedWord,
						userType,
					});
				}

                if (!auth?.auth?.ixl) {
                    if (util.isBowlActive(auth) || util.isBowlEnrollment(auth)) {
                        initAdsBowlSubscription({
                            adPurpose: AD_PURPOSE.DICTIONARY_BOWL,
                            cssClassname: '',
                            jContainer: $boxAdsBowlSubscription,
                            jQPreview: null,
                            targetWord: searchedWord,
                            userType,
                        });
                    }
                }

				VCOM.parse($boxCol2);
			}

			if (!VCOM || !VCOM.auth) {
				console.error('VCOM.auth is missing. Failed to init initAdsProgressPreviewQuiz.');
				return;
			}
			VCOM.auth(initAdsProgressPreviewQuiz);
		});
	});
</script>

</div>
</div>



<footer class="page-footer">

<nav class="sitelinks limited-width hide-mobile screen-only">
		<div class="lks-col">
			<div class="hdr-ftr-lk">Learn with us</div>
			<ul>
			<li><a href="/learner-subscription/">Learner subscriptions</a></li>
			<li><a href="/lists/">Vocabulary lists</a></li>
			<li><a href="/dictionary/">Dictionary</a></li>				
			<li><a href="/test-prep/">Test Prep</a></li>	
			<li><a href="/jam/">Join a Vocabulary Jam</a></li>
			<li><a href="/articles/commonly-confused-words/">Commonly confused words</a></li>
			<li><a href="/word-of-the-day/">Word of the day</a></li>
			</ul>				
		</div>
		<div class="lks-col">
			<div class="hdr-ftr-lk"><a href="/for-educators/">Teach with us</a></div>
			<ul>
			<li><a href="/for-educators/">For educators</a></li>
			<li><a href="/for-administrators/">For schools and districts</a></li>
			<li><a href="/how-it-works/">How it works</a></li>
			<li><a href="/membership/success-stories/">Success stories</a></li>
			<li><a href="/membership/research/">Research</a></li> 
			<li><a href="/professional-development/">Professional development</a></li> 
			<li><a href="/membership/quote/">Contact sales</a></li>
			</ul>				
		</div>
		<div class="lks-col">
			<div class="hdr-ftr-lk"><a href="/help/">Resources</a></div>
			<ul>
			<li><a href="/help/">Help articles/FAQ</a></li>			
			<li><a href="/teaching-resources/">Teaching resources</a></li>
			<li><a href="/learner-resource-center/">Learner resources</a></li>
			<li><a href="/english-language-learning-resources/">ESL/ELL resources</a></li>
			<li><a href="/lists/lists-by-grade/">Grade level resources</a></li>
			<li><a href="/resources/ipa-pronunciation/">IPA Pronunciation</a></li>
			<li><a href="/help/contactus">Contact support</a></li>
			</ul>				
		</div>
					
		<div class="lks-col">
			<div class="hdr-ftr-lk"><a href="/leaderboards/thisweek/">Leaderboards</a></div>
			<ul>
			<li><a href="/bowl/">Vocabulary Bowl</a></li>	
			<li><a href="/leaderboards/today/">Today's leaders</a></li>
			<li><a href="/leaderboards/thisweek/">Weekly leaders</a></li>
			<li><a href="/leaderboards/thismonth/">Monthly leaders</a></li>
			</ul>						
		</div>	
			
		<div class="lks-col">
			<div class="hdr-ftr-lk"><a href="/about/">About</a></div>
			<ul>
			<li><a href="/about/">Our Mission</a></li>
			<li><a href="/blog/">Blog</a></li>
			<li>
				<a href="https://www.ixl.com/feedback/vocabularydotcom"
					target="_blank">Tell us what you think</a>
			</li>
			<li><a href="/privacy/">Privacy Policy</a></li>
			<li><a href="/terms/">Terms of Use</a></li>
			</ul>				
		</div>

</nav>






<div class="ftr-legal">
	<div class="box-all-brands">
		<a class="lk-item-brand" href="https://www.ixl.com">
			<img src="https://cdn.vocabulary.com/images/footer/logo-ixl-for-ftr-190h5m.svg" alt="IXL Learning" class="img-ixl-brand-logo"/>
			<p>Comprehensive K-12 personalized learning</p>
		</a>
		<a class="lk-item-brand" href="https://www.rosettastone.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-rosetta-stone-for-ftr-cnz0xb.svg" alt="Rosetta Stone" class="img-rosetta-brand-logo"/>
			<p>Immersive learning for 25 languages</p>
		</a>
		<a class="lk-item-brand" href="https://www.wyzant.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-wyzant-for-ftr-92dn93.svg" alt="Wyzant" class="img-wyzant-brand-logo"/>
			<p>Trusted tutors ready to help in 300+ subjects</p>
		</a>
		<a class="lk-item-brand" href="https://www.education.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-education-com-for-ftr-a3xg4c.svg" alt="Education.com" class="img-education-brand-logo"/>
			<p>35,000 worksheets, games, and lesson plans</p>
		</a>
		<a class="lk-item-brand" href="https://www.teacherspayteachers.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-tpt-for-ftr-pa6bkm.svg" alt="TPT" class="img-tpt-brand-logo"/>
			<p>Marketplace for millions of educator-created resources</p>
		</a>
		<a class="lk-item-brand" href="https://www.abcya.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-abcya-for-ftr-1or2r2i.svg" alt="ABCya" class="img-abcya-brand-logo"/>
			<p>Fun educational games for kids</p>
		</a>
		<a class="lk-item-brand" href="https://www.spanishdict.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-spanish-dictionary-for-ftr-hev0u7.svg" alt="SpanishDictionary.com" class="img-spanish-dictionary-logo"/>
			<p>Spanish-English dictionary, translator, and learning</p>
		</a>
		<a class="lk-item-brand" href="https://www.ingles.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-ingles-for-ftr-w00ql8.svg" alt="Inglés.com" class="img-ingles-brand-logo"/>
			<p>Diccionario inglés-español, traductor y sitio de aprendizaje</p>
		</a>
		<a class="lk-item-brand" href="https://emmersion.ai/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-emmersion-for-ftr-1m00b4j.svg" alt="Emmersion" class="img-emmersion-brand-logo"/>
			<p>Fast and accurate language certification</p>
		</a>
		<a class="lk-item-brand" href="https://www.frenchdictionary.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-french-dictionary-for-ftr-nrqi20.svg" alt="FrenchDictionary.com" class="img-french-dictionary-logo"/>
			<p>French-English dictionary, translator, and learning</p>
		</a>
	</div><!-- end of DIV.ftr-ixl-brands -->
	<div class="box-ixl-brands-legal-lks">
		<div class="box-logo-txt-logo">
			<img src="https://cdn.vocabulary.com/images/footer/logo-vocab-green-check-for-ftr-4lic3k.svg" alt="vocabulary.com logo" class="logo-vocabulary"/>
			<div class="box-legal-text">
				<div class="box-copy-vocabulary">
					Copyright &copy; 2026 <br />
					Vocabulary.com, Inc.
				</div>
				<div class="box-division-rights">
					A division of IXL Learning <span class="txt-bull">&bull;</span> <br />
					All Rights Reserved.
				</div>
			</div>
			<img src="https://cdn.vocabulary.com/images/footer/logo-ixl-learning-ab1nek.svg" alt="IXL logo" class="logo-ixl"/>
		</div>
		<div class="box-social-media">
			<a class="lk-social-media"
				href="https://www.facebook.com/vocabularycom/"
				rel="noopener"
				target="_blank"
				title="Facebook"><img src="https://cdn.vocabulary.com/images/footer/facebook-fff-on-000-1djwcsu.svg" alt="Facebook logo" width="19" class="icon-facebook" height="19"/></a>
			<a class="lk-social-media"
				href="https://x.com/VocabularyCom/"
				rel="noopener"
				target="_blank"
				title="x.com"><img src="https://cdn.vocabulary.com/images/footer/x-fff-on-000-r417h3.svg" alt="X.com logo" width="19" class="icon-x" height="19"/></a>
			<a class="lk-social-media"
				href="https://www.instagram.com/vocabcom/"
				rel="noopener"
				target="_blank"
				title="Instagram"><img src="https://cdn.vocabulary.com/images/footer/instagram-fff-on-000-1nomn10.svg" alt="Instagram logo" width="19" class="icon-instagram" height="19"/></a>
			<a class="lk-social-media"
				href="https://www.linkedin.com/company/vocabulary-com/"
				rel="noopener"
				target="_blank"
				title="LinkedIn"><img src="https://cdn.vocabulary.com/images/footer/linkedin-fff-on-000-rszenv.svg" alt="LinkedIn logo" width="19" class="icon-linkedin" height="19"/></a>
		</div><!-- end of DIV.box-social-media -->
	</div><!-- end of DIV.box-ixl-brands-legal-lks -->
	
</div>





</footer>

<nav class="sitemap screen-only">
<div class="scrollable">
<div>
	<div class="sitelinks limited-width mobile-5050 pad2y">
	<div class="col9">
	<div class="col9">
		<div class="col4 pad1x">
			<div class="hdr-ftr-lk">Learn with us</div>
			<ul>
			<li><a href="/learner-subscription/">Learner subscriptions</a></li>
			<li><a href="/lists/">Vocabulary lists</a></li>
			<li><a href="/dictionary/">Dictionary</a></li>				
			<li><a href="/test-prep/">Test Prep</a></li>	
			<li><a href="/jam/">Join a Vocabulary Jam</a></li>
			<li><a href="/articles/commonly-confused-words/">Commonly confused words</a></li>
			<li><a href="/word-of-the-day/">Word of the day</a></li>
			</ul>				
		</div>
		<div class="col4 pad1x">
			<div class="hdr-ftr-lk"><a href="/for-educators/">Teach with us</a></div>
			<ul>
			<li><a href="/for-educators/">For educators</a></li>
			<li><a href="/for-administrators/">For schools and districts</a></li>
			<li><a href="/how-it-works/">How it works</a></li>
			<li><a href="/membership/success-stories/">Success stories</a></li>
			<li><a href="/membership/research/">Research</a></li> 
			<li><a href="/professional-development/">Professional development</a></li> 
			<li><a href="/membership/quote/">Contact sales</a></li>
			</ul>				
		</div>
		<div class="col4 pad1x">
			<div class="hdr-ftr-lk"><a href="/help/">Resources</a></div>
			<ul>
			<li><a href="/help/">Help articles/FAQ</a></li>			
			<li><a href="/teaching-resources/">Teaching resources</a></li>
			<li><a href="/learner-resource-center/">Learner resources</a></li>
			<li><a href="/english-language-learning-resources/">ESL/ELL resources</a></li>
			<li><a href="/lists/lists-by-grade/">Grade level resources</a></li>
			<li><a href="/resources/ipa-pronunciation/">IPA Pronunciation</a></li>
			<li><a href="/help/contactus">Contact support</a></li>
			</ul>				
		</div>
  </div>
  <div class="col9">
		<div class="col4 pad1x">
			<div class="hdr-ftr-lk"><a href="/leaderboards/thisweek/">Leaderboards</a></div>
			<ul>
			<li><a href="/bowl/">Vocabulary Bowl</a></li>	
			<li><a href="/leaderboards/today/">Today's leaders</a></li>
			<li><a href="/leaderboards/thisweek/">Weekly leaders</a></li>
			<li><a href="/leaderboards/thismonth/">Monthly leaders</a></li>
			</ul>						
		</div>	
		<div class="col4 pad1x">
			<div class="hdr-ftr-lk"><a href="/about/">About</a></div>
			<ul>
			<li><a href="/about/">Our Mission</a></li>
			<li><a href="/blog/">Blog</a></li>
			<li>
				<a href="https://www.ixl.com/feedback/vocabularydotcom"
					target="_blank">Tell us what you think</a>
			</li>
			<li><a href="/privacy/">Privacy Policy</a></li>
			<li><a href="/terms/">Terms of Use</a></li>
			</ul>	
		</div>
	</div>
	</div>
	
	<div class="col3 pad1x">
		
		<div class="loggedout-only clearfloat signinoptions">
			<div class="hdr-ftr-lk"><a href="/account/">My Account</a></div>
			<a role="button" class="sign-in button" href="/login/">Log in</a>
			<a role="button" class="sign-up button green" href="/signup/">Sign up</a>
		</div>
		<ul class="account-menu loggedin-only">
			
			<div class="hdr-ftr-lk"><a href="/account/">My Account</a></div>
			<li><a href="/auth/logout"><i class="ss-logout"></i>Log Out</a></li>
			<li class="nav-my-learning"><a href="/learner/"><i class="ss-dashboard"></i>My Learning</a></li>
			<li class="nav-proficiency-report"><a href="/learner-subscription/"><i class="icon"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M3.79581 10.4049L6.5 12.5L4.68541 15.6755C4.60616 15.8142 4.40431 15.8086 4.33287 15.6657L3.5 14H1.40889C1.24247 14 1.14885 13.8086 1.25101 13.6772L3.79581 10.4049ZM12.2042 10.4049L14.749 13.6772C14.8511 13.8086 14.7575 14 14.5911 14H12.5L11.6671 15.6657C11.5957 15.8086 11.3938 15.8142 11.3146 15.6755L9.5 12.5L12.2042 10.4049Z" fill="white"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M8 1.85668L7.17743 2.4567C6.83411 2.70714 6.41994 2.84171 5.99498 2.8409L4.97683 2.83897L4.66404 3.80789C4.53349 4.2123 4.27752 4.56461 3.93324 4.81374L3.1084 5.41063L3.42487 6.37835C3.55696 6.78226 3.55696 7.21775 3.42487 7.62166L3.1084 8.58938L3.93324 9.18627C4.27752 9.4354 4.53349 9.78771 4.66404 10.1921L4.97683 11.161L5.99498 11.1591C6.41994 11.1583 6.83411 11.2929 7.17743 11.5433L8 12.1433L8.82256 11.5433C9.16589 11.2929 9.58006 11.1583 10.005 11.1591L11.0232 11.161L11.336 10.1921C11.4665 9.78771 11.7225 9.4354 12.0668 9.18627L12.8916 8.58938L12.5751 7.62166C12.443 7.21775 12.443 6.78226 12.5751 6.37835L12.8916 5.41063L12.0667 4.81374C11.7225 4.56461 11.4665 4.2123 11.336 3.80789L11.0232 2.83897L10.005 2.8409C9.58006 2.84171 9.16589 2.70714 8.82256 2.4567L8 1.85668ZM8.29466 0.214948C8.11909 0.0868792 7.8809 0.0868793 7.70534 0.214948L6.29345 1.24486C6.20762 1.30747 6.10407 1.34111 5.99783 1.34091L4.25023 1.33758C4.03291 1.33717 3.84021 1.47717 3.77345 1.68398L3.23658 3.34708C3.20394 3.44818 3.13995 3.53626 3.05388 3.59854L1.63808 4.62307C1.46203 4.75047 1.38842 4.977 1.45597 5.18355L1.99917 6.84459C2.0322 6.94557 2.0322 7.05444 1.99917 7.15542L1.45597 8.81646C1.38842 9.02301 1.46203 9.24955 1.63808 9.37694L3.05388 10.4015C3.13995 10.4638 3.20394 10.5518 3.23658 10.6529L3.77345 12.316C3.84021 12.5228 4.03291 12.6628 4.25023 12.6624L5.99783 12.6591C6.10407 12.6589 6.20762 12.6925 6.29345 12.7552L7.70534 13.7851C7.8809 13.9131 8.11909 13.9131 8.29466 13.7851L9.70655 12.7552C9.79238 12.6925 9.89592 12.6589 10.0022 12.6591L11.7498 12.6624C11.9671 12.6628 12.1598 12.5228 12.2265 12.316L12.7634 10.6529C12.7961 10.5518 12.86 10.4638 12.9461 10.4015L14.3619 9.37694C14.538 9.24955 14.6116 9.02301 14.544 8.81646L14.0008 7.15542C13.9678 7.05444 13.9678 6.94557 14.0008 6.84459L14.544 5.18355C14.6116 4.977 14.538 4.75047 14.3619 4.62307L12.9461 3.59854C12.86 3.53626 12.7961 3.44818 12.7634 3.34708L12.2265 1.68398C12.1598 1.47717 11.9671 1.33717 11.7498 1.33758L10.0022 1.34091C9.89592 1.34111 9.79238 1.30747 9.70655 1.24486L8.29466 0.214948Z" fill="white"/>
</svg></i>My Proficiency Report</a></li>
			<li class="nav-myprofile"><a href="/profiles/my"><i class="ss-user"></i>My Profile</a></li>
			<li class="perms-school-reports-only"><a href="/account/schools"><i class="ss-school ss-symbolicons-block"></i>Schools &amp; Teachers</a></li>
			
			<li class="nav-classes educator-only"><a href="/account/classes"><i class="ss-users"></i>My Classes</a></li>
			
			<li class="nav-assignments"><a href="/account/activities/"><i class="ss-attach"></i>Assignments &amp; Activities</a></li>
			
			<li ><a href="/account/lists/"><i class="ss-list"></i>My Lists</a>
			<ul>
				<li><a href="/lists/"><i class="ss-search"></i>Find a List to Learn...</a></li>
				<li><a href="/lists/new"><i class="ss-hospital ss-symbolicons-block"></i>Create a New List...</a></li>
			</ul>
			</li>
			<li><a href="/progress/"><i class="ss-barchart"></i>My Progress</a>
				<ul>
					<li><a href="/account/progress/words/learning"><i class="ss-hiker ss-symbolicons-block"></i>Words I'm Learning</a></li>
					<li><a href="/account/progress/words/trouble"><i class="ss-bullseye ss-symbolicons-block"></i>My Trouble Words</a></li>
					<li><a href="/account/progress/words/mastered"><i class="ss-check ss-symbolicons-block"></i>Words I've Mastered</a></li>
					<li><a href="/account/progress/achievements"><i class="ss-award ss-symbolicons-block"></i>My Achievements</a></li>
				</ul>
			</li>	
			<li class="perms-user-admin-only"><a href="/account/users"><i class="ss-usergroup ss-symbolicons-block "></i>User Administration</a></li>
			<li class="perms-auth-admin-only"><a href="/account/authentication"><i class="ss-key"></i>User Authentication</a></li>
			<li>
				<a href="/account/"><i class="ss-settings"></i>My Account</a>			
			</li>
			
		</ul>
	</div>
	</div>
	





<div class="ftr-legal">
	<div class="box-all-brands">
		<a class="lk-item-brand" href="https://www.ixl.com">
			<img src="https://cdn.vocabulary.com/images/footer/logo-ixl-for-ftr-190h5m.svg" alt="IXL Learning" class="img-ixl-brand-logo"/>
			<p>Comprehensive K-12 personalized learning</p>
		</a>
		<a class="lk-item-brand" href="https://www.rosettastone.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-rosetta-stone-for-ftr-cnz0xb.svg" alt="Rosetta Stone" class="img-rosetta-brand-logo"/>
			<p>Immersive learning for 25 languages</p>
		</a>
		<a class="lk-item-brand" href="https://www.wyzant.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-wyzant-for-ftr-92dn93.svg" alt="Wyzant" class="img-wyzant-brand-logo"/>
			<p>Trusted tutors ready to help in 300+ subjects</p>
		</a>
		<a class="lk-item-brand" href="https://www.education.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-education-com-for-ftr-a3xg4c.svg" alt="Education.com" class="img-education-brand-logo"/>
			<p>35,000 worksheets, games, and lesson plans</p>
		</a>
		<a class="lk-item-brand" href="https://www.teacherspayteachers.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-tpt-for-ftr-pa6bkm.svg" alt="TPT" class="img-tpt-brand-logo"/>
			<p>Marketplace for millions of educator-created resources</p>
		</a>
		<a class="lk-item-brand" href="https://www.abcya.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-abcya-for-ftr-1or2r2i.svg" alt="ABCya" class="img-abcya-brand-logo"/>
			<p>Fun educational games for kids</p>
		</a>
		<a class="lk-item-brand" href="https://www.spanishdict.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-spanish-dictionary-for-ftr-hev0u7.svg" alt="SpanishDictionary.com" class="img-spanish-dictionary-logo"/>
			<p>Spanish-English dictionary, translator, and learning</p>
		</a>
		<a class="lk-item-brand" href="https://www.ingles.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-ingles-for-ftr-w00ql8.svg" alt="Inglés.com" class="img-ingles-brand-logo"/>
			<p>Diccionario inglés-español, traductor y sitio de aprendizaje</p>
		</a>
		<a class="lk-item-brand" href="https://emmersion.ai/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-emmersion-for-ftr-1m00b4j.svg" alt="Emmersion" class="img-emmersion-brand-logo"/>
			<p>Fast and accurate language certification</p>
		</a>
		<a class="lk-item-brand" href="https://www.frenchdictionary.com/">
			<img src="https://cdn.vocabulary.com/images/footer/logo-french-dictionary-for-ftr-nrqi20.svg" alt="FrenchDictionary.com" class="img-french-dictionary-logo"/>
			<p>French-English dictionary, translator, and learning</p>
		</a>
	</div><!-- end of DIV.ftr-ixl-brands -->
	<div class="box-ixl-brands-legal-lks">
		<div class="box-logo-txt-logo">
			<img src="https://cdn.vocabulary.com/images/footer/logo-vocab-green-check-for-ftr-4lic3k.svg" alt="vocabulary.com logo" class="logo-vocabulary"/>
			<div class="box-legal-text">
				<div class="box-copy-vocabulary">
					Copyright &copy; 2026 <br />
					Vocabulary.com, Inc.
				</div>
				<div class="box-division-rights">
					A division of IXL Learning <span class="txt-bull">&bull;</span> <br />
					All Rights Reserved.
				</div>
			</div>
			<img src="https://cdn.vocabulary.com/images/footer/logo-ixl-learning-ab1nek.svg" alt="IXL logo" class="logo-ixl"/>
		</div>
		<div class="box-social-media">
			<a class="lk-social-media"
				href="https://www.facebook.com/vocabularycom/"
				rel="noopener"
				target="_blank"
				title="Facebook"><img src="https://cdn.vocabulary.com/images/footer/facebook-fff-on-000-1djwcsu.svg" alt="Facebook logo" width="19" class="icon-facebook" height="19"/></a>
			<a class="lk-social-media"
				href="https://x.com/VocabularyCom/"
				rel="noopener"
				target="_blank"
				title="x.com"><img src="https://cdn.vocabulary.com/images/footer/x-fff-on-000-r417h3.svg" alt="X.com logo" width="19" class="icon-x" height="19"/></a>
			<a class="lk-social-media"
				href="https://www.instagram.com/vocabcom/"
				rel="noopener"
				target="_blank"
				title="Instagram"><img src="https://cdn.vocabulary.com/images/footer/instagram-fff-on-000-1nomn10.svg" alt="Instagram logo" width="19" class="icon-instagram" height="19"/></a>
			<a class="lk-social-media"
				href="https://www.linkedin.com/company/vocabulary-com/"
				rel="noopener"
				target="_blank"
				title="LinkedIn"><img src="https://cdn.vocabulary.com/images/footer/linkedin-fff-on-000-rszenv.svg" alt="LinkedIn logo" width="19" class="icon-linkedin" height="19"/></a>
		</div><!-- end of DIV.box-social-media -->
	</div><!-- end of DIV.box-ixl-brands-legal-lks -->
	
		<a href="/auth/admin"
			rel="nofollow"
			hidden="hidden"
			aria-hidden="true"
			style="position: absolute; top: 0px; left: -1000px; width:1px; height:1px">
				<img src="https://cdn.vocabulary.com/images/clear-16y9b5d.gif" width="0" alt="" aria-hidden="true" height="0"/>
		</a>
	
</div>





</div></div>
</nav>
</div>
<div class="scroll-tracking-pixel"></div>



<script>(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.innerHTML="window.__CF$cv$params={r:'a19e01fcd8ecf7a5',t:'MTc4MzgzNzkxNQ=='};var a=document.createElement('script');a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'loading'!==document.readyState&&(document.onreadystatechange=e,c())}}}})();</script></body>
</html>
		
"""


def test_parse_sentences():
    json_obj = json.loads(json_str_word_good)
    sentences = vcom.parse_sentences(json_obj)

    assert len(sentences) == 4

    sentence4 = sentences[3]
    assert sentence4['offsets'] == (33, 37)
    assert sentence4['sentence'] == '“Will’s going to do it! You’re a good man, George!”'
    assert sentence4['author'] == 'Jewell Parker Rhodes'
    assert sentence4['title'] == 'Will’s Race for Home'
    assert sentence4['date'] == 1735689600000


def test_parse_page_word_good():

    vcom_word = vcom.make_empty_vcomword('good')
    vcom.parse_page(html_str_word_good, vcom_word)

    assert vcom_word['phonetics_us'] == '/gʊd/'
    assert vcom_word['phonetics_uk'] == '/gʊd/'
    assert vcom_word['pron_audio_us'] == 'https://audio.vocabulary.com/1.0/us/G/1C361RWL0RWKM.mp3'
    assert (
        vcom_word['pron_audio_uk']
        == 'https://sd-pronunciation-processed-videos.sdcdns.com/desktop/lang_en_pron_4348_speaker_8_syllable_all_version_50.mp4'
    )
    assert (
        vcom_word['funny_def_short']
        == """We all know what <i>good</i> means as an adjective––pleasing, favorable, nice. But did you know that <i>good</i> is also a noun, meaning something that can be sold? This means a shopkeeper’s ideal is to have really <i>good goods</i>."""
    )
    assert (
        vcom_word['funny_def_long']
        == """<i>Good</i> comes from an old German root for gathering, and in its original sense it means that something fits well. If something is good for you, it fits you well, or is healthy for you to eat. A long walk through a crowded city is good for someone who likes people-watching, but if you are a misanthrope and you hate people, that wouldn't be so good. If food has spoiled, it’s no longer good."""
    )

    defs = vcom_word['definitions']
    assert len(defs) == 27

    # def2 has special case in `synonyms`
    def2 = defs[1]
    assert def2['pos'] == 'adj'
    assert len(def2['example']) == 1
    assert len(def2['synonyms']) == 2

    def27 = defs[26]
    assert def27['pos'] == 'n'
    assert len(def27['types']) == 39
    assert len(def27['type of']) == 1

    wfs = vcom_word['word_family']
    assert len(wfs) == 17

    wf1 = wfs[0]
    assert wf1['word'] == 'good'
    assert wf1['freq'] == 4


def test_vcom_funny_api(monkeypatch):
    mock_helper.mock_session_get(monkeypatch, vcom._session, html_str_word_good, json.loads(json_str_word_good))
    word_data = vcom_funny.API.query('good')

    assert word_data is not None
    assert word_data['term'] == 'good'
    assert word_data['definition'] == [
        """<div>1 <span class="pos-adj">adj</span> <span class="pos-n">n</span> <span class="pos-adv">adv</span> 2 <span class="pos-adj">adj</span> <span class="pos-adv">adv</span> 3 <span class="pos-adj">adj</span> 4 <span class="pos-n">n</span></div><p>We all know what <i>good</i> means as an adjective––pleasing, favorable, nice. But did you know that <i>good</i> is also a noun, meaning something that can be sold? This means a shopkeeper’s ideal is to have really <i>good goods</i>.</p><p><i>Good</i> comes from an old German root for gathering, and in its original sense it means that something fits well. If something is good for you, it fits you well, or is healthy for you to eat. A long walk through a crowded city is good for someone who likes people-watching, but if you are a misanthrope and you hate people, that wouldn't be so good. If food has spoiled, it’s no longer good.</p>"""
    ]
    assert len(word_data['sentence']) == 4
    assert word_data['AmEPhonetic'] == '/gʊd/'
    assert word_data['AmEPron'] == 'https://audio.vocabulary.com/1.0/us/G/1C361RWL0RWKM.mp3'
    assert word_data['BrEPhonetic'] == '/gʊd/'
