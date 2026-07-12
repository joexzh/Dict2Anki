# vocabulary.com web api scheme

## source

Data is fetch from

- word page: <https://www.vocabulary.com/dictionary/{word}>
- pronounce: <https://audio.vocabulary.com/1.0/us/{data-audio}.mp3>
- sentence: <https://corpus.vocabulary.com/api/1.0/examples/random.json?maxResults=64&query={word}&startOffset=0>

## json scheme

```jsonc
// example word: mother
{
  "word": "mother",
  "phonetics_us": "/ˈmʌðər/",
  "phonetics_uk": "/ˈmʌðə/",
  "pron_audio_us": "https://audio.vocabulary.com/1.0/us/M/TQUUPG43XUCM.mp3",
  // have to convert mp4 to mp3
  "pron_audio_uk": "https://sd-pronunciation-processed-videos.sdcdns.com/desktop/lang_en_pron_4983_speaker_8_syllable_all_version_50.mp4",

  // funny short definition
  "funny_def_short": "this is html <p> block",

  // funny long definition
  "funny_def_long": "this is html <p> block",

  // definition list
  "definitions": [
    {
      "pos": "noun", // part of speech
      "pos_color": "#0FA646",
      "definition": "a woman who has given birth to a child (also used as a term of address to your mother)",
      "example": ["the <strong>mother</strong> of three children"],
      "synonyms": [{"words": ["str"], "definition": "" }],
      "antonyms": [{
        "words": ["father"],
        "definition": "a male parent (also used as a term of address to your father)",
      }],
      "examples": [{
        "words": ["Blessed Virgin"],
        "definition": "the mother of Jesus; Christians refer to her as the Virgin Mary; she is especially honored by Roman Catholics",
      }],
      "types": [{
        "words": ["ma", "mama", "mamma", "mammy", "mom", "momma", "mommy", "mum", "mummy"],
        "definition": "informal terms for a mother"
      }],
      "type of": [{
        "words": ["parent"],
        "definition": "a father or mother; one who begets or one who gives birth to or nurtures and raises a child; a relative who plays the role of guardian"
      }],
    },
  ],

  "word_family": [
    {
      "word": "mother",
      "freq": 14, // you will encounter this word once every 14 pages.
      "children": [{
        "word": "mothers",
        "freq": 300,
        "children": []
      }]
    }
  ],

  "sentences": [
    {
      "sentence": "Next, if you wanted some peculiar person to ride by, there might have come a crusader who had promised to deliver the grave of God.",
      "author": "T. H. White",
      "title": "The Once and Future King",
      "date": 1268611200000
    },
  ]
}
```

## html parse logic for each field

Pseudo JavaScript code:

``` javascript
const word_area = document.querySelector('.word-area')

 // `word`: get the text content of it
const word = document.querySelector('#hdr-word-area');

const ipas = word_area.querySelectorAll('.ipa-section .ipa-with-audio');
const ipa_first = ipas[0];

// `phoneetics_us`: get the text content of it
const phonetics_us = ipa_first.querySelector('.span-replace-h3');

// `pron_audio_us`: combine the http prefix and data-audio
const pron_audio_us = ipa_first.querySelector('.audio').getAttribute('data-audio');

const ipa_second = ipas[1];

 // `phonetics_us`: get the text content of it
const phonetics_uk = ipa_second.querySelector('.span-replace-h3');

// `pron_audio_uk`: unsupported, it's a MP4 file.

// `funny_def_short`: get the html content of it
const funny_def_short = word_area.querySelector('.short');

// `funny_def_long`: get the html content of it
const funny_def_long = word_area.querySelector('.long');

const def_lis = document.querySelectorAll('.word-definitions > ol > li');

// ===---for each def_li begin---===

const def_li = def_lis[0];
const def_li_def = def_li.querySelector('.definition');

// `pos`: get the text content of it
const pos_el = def_li_def.querySelector('.pos-icon');

// also set the pos color

// `def`: get the text content of it
const def_el = Array.from(def_li_def.childNodes)
  .filter(node => node.nodeType === Node.TEXT_NODE)
  .map(node => node.textContent.trim())
  .join('');

const def_li_content = def_li.querySelector('.defContent');

// `example`: get the html content of it
const example_els = def_li_content.querySelectorAll(':scope > .example');

const instances_els = def_li_content.querySelectorAll(':scope > .instances');

// `synonyms`: complex html parse logic
let synonyms = [];

// for each instances_el
if (const dd_els = instances_el.querySelectorAll(':scope > .div-replace-dd ')) {
  // if expandable, skip the first 2 elements, for "types:" special case
  if (dd_els.length > 0 && dd_els[0].classList.contains('more')) {
    dd_els = [...dd_els].slice(2);
  }

  // for each dd_el
  const dd_el = dd_els[0];
  // get the text content of the words
  const words = dd_el.querySelectorAll('a.word');
  // get the text content of it
  const def = dd_el.querySelector('.definition');

} else {
  const words = instances.el.querySelectorAll('a.word');

  // add the words as a record of synonyms, no definition
}

const more_info_instances = def_li_content.querySelectorAll(':scope > .more-info-section > .more-info > .instances');

// ===---for each more_info_instances start---===

const more_info_instance = more_info_instances[0];
const info_type = more_info_instance.querySelector('.detail').textContent;
if (info_type === 'antonyms:/examples:/types:/type_of:') {
  // set field to info_type
}

// the logic the set field value is the same as `synonyms`

// ===---for each more_info_instances end---===

// ===---for each def_li end---===

// `word_family`: see [[## word family]]
const wf_el = document.querySelector('vcom\\:wordfamily');
const wf_json = JSON.parse(el.getAttribute('data'));

// `sentences`: see  [[## sentences]], take the first 4 sentences.
```

## word family data

``` json
[
{"word":"mother","hw":true,"freq":274.38791166087805,"ffreq":293.1609183344688,"type":0},
{"word":"mothers","parent":"mother","freq":13.911132651618884,"ffreq":13.911132651618884,"type":1},
{"word":"motherly","hw":true,"parent":"mother","freq":1.831917310381049,"ffreq":1.906371736444938,"type":2},
{"word":"motherhood","hw":true,"parent":"mother","freq":1.6826700290438898,"ffreq":1.6840237458814151,"type":3},
{"word":"motherless","hw":true,"parent":"mother","freq":0.845734594243902,"ffreq":0.845734594243902,"type":2},
{"word":"mothering","parent":"mother","freq":0.21253354349146478,"ffreq":0.21253354349146478,"type":1},
{"word":"mothered","parent":"mother","freq":0.1725988967844698,"ffreq":0.1725988967844698,"type":1},
{"word":"motherliness","hw":true,"parent":"motherly","freq":0.07445442606388893,"ffreq":0.07445442606388893,"type":2},
{"word":"foremothers","parent":"foremother","freq":0.027751195169267693,"ffreq":0.027751195169267693,"type":1},
{"word":"motherlike","hw":true,"parent":"mother","freq":0.009476017862676774,"ffreq":0.009476017862676774,"type":4},
{"word":"foremother","hw":true,"parent":"mother","freq":0.003384292093813133,"ffreq":0.031135487263080824,"type":4},
{"word":"motherhoods","parent":"motherhood","freq":0.0013537168375252534,"ffreq":0.0013537168375252534,"type":1}
]
```

### calculate freq

According to <https://cdn.vocabulary.com/js/vcom/wordfamily-1jcjb8e.js>,

``` javascript
var d = (1 + parseInt("" + 1 / (c / 4E3))).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
```

`c` is "ffreq".

## part of speech (pos) class name map

```python
{
    'pos_n': {'name': 'n', 'color': '#0FA646'},
    'pos_v': {'name': 'v', 'color': '#CD4D03'},
    'pos_a': {'name': 'adj', 'color': '#007BC4'},
    'pos_r': {'name': 'adv', 'color': '#7B61FF'},
    'pos_pron': {'name': 'pron', 'color': '#44AA02'},
    'pos_prep': {'name': 'prep', 'color': '#BE6DCF'},
    'pos_conj': {'name': 'conj', 'color': '#CF8300'},
    'pos_interj': {'name': 'interj', 'color': '#FA52B7'},
    'pos_art': {'name': 'art', 'color': '#ED5362'},
    'pos_idm': {'name': 'idm', 'color': '#00A886'},
    'pos_abbr': {'name': 'abbr', 'color': '#EB7302'},
}
```

## sentences

Fetch URL: <https://corpus.vocabulary.com/api/1.0/examples/random.json?maxResults=64&query=crusader&startOffset=0>

Also have other URLS:

- literature:  https://corpus.vocabulary.com/api/1.0/examples.json?maxResults=24&query=crusader&startOffset=0&domain=F
- arts/culture:  https://corpus.vocabulary.com/api/1.0/examples.json?maxResults=24&query=crusader&startOffset=0&domain=A
- news:  https://corpus.vocabulary.com/api/1.0/examples.json?maxResults=24&query=crusader&startOffset=0&domain=N
- business:  https://corpus.vocabulary.com/api/1.0/examples.json?maxResults=24&query=crusader&startOffset=0&domain=B
- sports:  https://corpus.vocabulary.com/api/1.0/examples.json?maxResults=24&query=crusader&startOffset=0&domain=S
- science/med: https://corpus.vocabulary.com/api/1.0/examples.json?maxResults=24&query=crusader&startOffset=0&domain=M

But we use the random API only.

Remote json scheme, example word "crusader":

``` jsonc
{
  "sentences": [
    {
      "corpusId": "LIT",
      "offsets": [
        75,
        84
      ],
      "sentence": "Royal had read of the man’s exploits in the newspaper—lawyer, abolitionist crusader, bane of slavers and those who did their dirty work.",
      "volume": {
        "asin": "0385542364",
        "author": "Colson Whitehead", // author name
        "corpus": {
          "id": "LIT",
          "name": "Literature"
        },
        "dateAdded": 1516744234387,
        "datePublished": 1470096000000, // compute it to year
        "domain": "F",
        "domains": [
          "F"
        ],
        "id": 4000512,
        "isbn": "9780385542364",
        "sentenceCount": 6298,
        "title": "The Underground Railroad: A Novel", // citation name
        "wordCount": 86874
      },
      "volumeId": 4000512,
      "volumeOffset": 5366
    },
    {
      "corpusId": "LIT",
      "offsets": [
        103,
        111
      ],
      "sentence": "What’s more, here was a way for Hoover, a deskbound functionary, to cast himself as a dashing figure—a crusader for the modern scientific age.",
      "volume": {
        "asin": "0307742482",
        "author": "David Grann",
        "corpus": {
          "id": "LIT",
          "name": "Literature"
        },
        "dateAdded": 1597937534829,
        "datePublished": 1492473600000,
        "domain": "F",
        "domains": [
          "F"
        ],
        "id": 5467904,
        "isbn": "9780307742483",
        "sentenceCount": 3719,
        "title": "Killers of the Flower Moon",
        "wordCount": 75151
      },
      "volumeId": 5467904,
      "volumeOffset": 2032
    },
    {
      "corpusId": "LIT",
      "offsets": [
        20,
        29
      ],
      "sentence": "He saw himself as a crusader, a champion of the underdog, an enemy of sinister authority.",
      "volume": {
        "asin": "0393338827",
        "author": "Michael Lewis",
        "corpus": {
          "id": "LIT",
          "name": "Literature"
        },
        "dateAdded": 1762884839876,
        "datePublished": 1268611200000,
        "domain": "A",
        "domains": [
          "A"
        ],
        "id": 6748699,
        "isbn": "9780393338829",
        "sentenceCount": 3904,
        "title": "The Big Short",
        "wordCount": 82419
      },
      "volumeId": 6748699,
      "volumeOffset": 2316
    },
    {
      "corpusId": "LIT",
      "offsets": [
        77,
        85
      ],
      "sentence": "Next, if you wanted some peculiar person to ride by, there might have come a crusader who had promised to deliver the grave of God.",
      "volume": {
        "asin": "0441627404",
        "author": "T. H. White",
        "corpus": {
          "id": "LIT",
          "name": "Literature"
        },
        "dateAdded": 1470155460313,
        "datePublished": -378691200000,
        "domain": "F",
        "domains": [
          "F"
        ],
        "id": 3111240,
        "isbn": "9780441627400",
        "sentenceCount": 11781,
        "title": "The Once and Future King",
        "wordCount": 236358
      },
      "volumeId": 3111240,
      "volumeOffset": 9496
    }
  ],
  "totalHits": 879
}
```
