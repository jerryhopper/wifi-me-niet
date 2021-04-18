<?php

use Pachico\SlimSwoole\BridgeManager;
use Respect\Validation\Validator as v;
use Slim\Http;
use Slim\Container;

require __DIR__ . '/../app/vendor/autoload.php';


// Enable the hook for MySQL: PDO/MySQLi
Co::set(['hook_flags' => SWOOLE_HOOK_TCP]);


use GuzzleHttp\Client;
use GuzzleHttp\HandlerStack;
use GuzzleHttp\Middleware;
use Yurun\Util\Swoole\Guzzle\SwooleHandler;


$app = new \Slim\App(['settings' => ["displayErrorDetails"=>true]]);

//print getenv("APP_DBNAME")

$container = $app->getContainer();

$container['pdo'] = function (Container $container) {
    // better load the settings with $container->get('settings')
    $host = getenv("APP_DBHOST");
    $dbname = getenv("APP_DBNAME");
    $username = getenv("APP_DBUSER");
    $password = getenv("APP_DBPASS");
    $charset = 'utf8';
    $collate = 'utf8_unicode_ci';
    $dsn = "mysql:host=$host;dbname=$dbname;charset=$charset";
    $options = [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_PERSISTENT => false,
        PDO::ATTR_EMULATE_PREPARES => false,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES $charset COLLATE $collate"
    ];

    return new PDO($dsn, $username, $password, $options);
};

$container['view'] = function ($container) {
    $view = new \Slim\Views\Twig('templates', [
        'cache' => false /*'path/to/cache'*/
    ]);

    // Instantiate and add Slim specific extension
    $router = $container->get('router');
    $uri = \Slim\Http\Uri::createFromEnvironment(new \Slim\Http\Environment($_SERVER));
    $view->addExtension(new \Slim\Views\TwigExtension($router, $uri));

    return $view;
};


function setupdatabase(){
    $host = getenv("APP_DBHOST");
    $username = getenv("APP_DBUSER");
    $password = getenv("APP_DBPASS");
    $dbname = getenv("APP_DBNAME");

    $dsn = "mysql:host=$host;charset=utf8";
    $pdo = new PDO($dsn, $username, $password);


    $stmt = $pdo->prepare("SHOW DATABASES WHERE `database`=:database");
    $stmt->execute(['database' => $dbname ]);
    $result = $stmt->fetch();
    return $result;

    #$sql = str_replace("###DBNAME###",$dbname,file_get_contents('file.sql'));
    #$qr = $pdo->exec($sql);
}

/*
    Functions
*/

function dnt($mac,$pdo){

    error_log("optOut");

    $datetime=date('Y-m-d H:i:s');
    $data = [
        'datetime' => $datetime,
        'machash' => dohash($mac),

    ];

    try {
        $sql = "INSERT INTO dntmacs (datetime,machash) VALUES (:datetime,:machash)";
        $stmt= $pdo->prepare($sql);
        $stmt->execute($data);
    }catch(Exception $e){
        error_log($e->getMessage());
    }

}

function optOut($mac,$pdo){
    //getStatus($mac,$pdo);
    error_log("optOut");

    $datetime=date('Y-m-d H:i:s');
    $data = [
        'datetime' => $datetime,
        'machash' => dohash($mac),
    ];

    try {
        $sql = "INSERT INTO optout (datetime,machash) VALUES (:datetime,:machash)";
        $stmt= $pdo->prepare($sql);
        $stmt->execute($data);
    }catch(Exception $e){
        error_log($e->getMessage());
    }

}

function getStatus($mac,$pdo){

    $machash = dohash($mac);

    // dntmac
    $stmt = $pdo->prepare("SELECT id,datetime FROM dntmacs WHERE machash=:machash");
    $stmt->execute(['machash' => $machash]);
    $dntmac = $stmt->fetch();


    // optout
    $stmt = $pdo->prepare("SELECT id,datetime FROM optout WHERE machash=:machash");
    $stmt->execute(['machash' => $machash]);
    $optout = $stmt->fetch();


    return array("optout"=>$optout,"dntmac"=>$dntmac);
}

function dohash( $mac,$secret="secret" ){

    // Create a ripehash using our secret.
    $ripehash = hash_hmac('ripemd160', str_replace(":","",strtoupper($mac)), $secret );

    // get the last 2 chars from the ripehash.
    $hash_append = substr($ripehash, -2, 2);

    // hash again using sha256, we need a loooong hashvalue
    $shahash = hash("sha256",$ripehash);

    // to anonimize, we remove the last 2 chars from the hash.
    $shortenedHash = substr($shahash, 0, -2);

    // glue the shortened sha-hash with the last 2 chars from the ripehash to 'anonymize' the mac.
    $finalhash = strtolower($shortenedHash.$hash_append);

    // return the hash!
    return $finalhash;
}

function DoNotFollow($pdo,$macid,$statuscode,$location){
    error_log("DoNotFollow");
    $loc= strtoupper($location);

    if( $loc == strtoupper("ThanksRegistration.html")){
        # mac added to moa-optout.
        error_log("MOA: ThanksRegistration.html");
        dnt($macid,$pdo);

    }elseif ( strpos($location,strtoupper($macid) ) !==false ){
        # already exists
        error_log("MOA: Already exists");
        dnt($macid,$pdo);

    }else{
        # dunno what went wrong.
        error_log("MOA: Huh?");
    }


}


/*
    Endpoints
*/

$app->get('/api/oui[/{macAddress}]', function (Http\Request $request, Http\Response $response, array $args) {
    if (!v::macAddress()->validate($args['macAddress'])) {
        return $response->withJson(["error" => "Invalid macaddress", "mac" => $args['macAddress']])->withStatus(500);
    }
    $data = oui($args['macAddress'],"no");
    return $response->withJson($data);
});


$app->get('/api/status[/{macAddress}]', function (Http\Request $request, Http\Response $response, array $args) {
    if( ! v::macAddress()->validate($args['macAddress']) ){
        return $response->withJson(["error"=>"Invalid macaddress","mac"=>$args['macAddress']])->withStatus(500);
    }

    $pdo = $this->get('pdo');

    $macid=strtoupper($args['macAddress']);//'C4:3A:35:2E:B8:4D';

    $result = getStatus($macid,$pdo);

    return $response->withJson($result);
});


$app->get('/api/optout[/{macAddress}]', function (Http\Request $request, Http\Response $response, array $args) {
    if( ! v::macAddress()->validate($args['macAddress']) ){
        return $response->withJson(["error"=>"Invalid macaddress"])->withStatus(500);
    }

    $pdo = $this->get('pdo');

    $macid=strtoupper($args['macAddress']);//'C4:3A:35:2E:B8:4D';



    $status = getStatus($macid,$pdo);
    if($status['dntmac'] !== false ){
        return $response->withJson(["error"=>"mac exists"]);
    }
    if($status['optout'] !== false ){
        return $response->withJson(["error"=>"optedout"]);
    }

    $result = optOut($macid,$pdo);

    return $response->withJson(["result"=>"ok"]);

});


$app->get('/api/donotfollow[/{macAddress}]', function (Http\Request $request, Http\Response $response, array $args) {
    if( ! v::macAddress()->validate($args['macAddress']) ){
        return $response->withJson(["error"=>"Invalid macaddress"])->withStatus(500);
    }

    $pdo = $this->get('pdo');

    $macid=strtoupper($args['macAddress']);//'C4:3A:35:2E:B8:4D';

    $result = getStatus($macid,$pdo);


    if( $result['dntmac']!==false ){
        return $response->withJson(["error"=>"mac exists"]);
    }

    if( $result['optout']!==false ){
        return $response->withJson(["error"=>"optout"]);
    }




    go(function() use ($macid,$pdo) {

        $container = [];
        $history = Middleware::history($container);

        $handler = new SwooleHandler();
        $stack = HandlerStack::create($handler);
        $stack->push($history);

        $client = new Client([ 'handler' => $stack,
            'allow_redirects' => ['track_redirects' => true]
        ]);

        $request = $client->post('https://www.wifi-me-niet.nl/regprocess.php', [
            'verify'    =>  true,
            'form_params' => [
                'macid' =>[$macid],
                'email' => getenv("APP_UNSUBEMAIL"),
                'phone' => getenv("APP_UNSUBPHONE"),
                'radio2' => 'on',
                'remind' => 'non',
                'frequency' => 'drm',

            ]
        ]);

        $statuscode = $container[0]['response']->getStatusCode();
        $location   = $container[0]['response']->getHeaders()['location'][0];

        DoNotFollow($pdo,$macid,$statuscode,$location);
    });

    return $response->withJson(["status"=>"pending"]);
});


$app->get('/test', function (Http\Request $request, Http\Response $response, array $args) {

    return $response->write("");
});

$app->get('/', function (Http\Request $request, Http\Response $response, array $args) {

    return $this->view->render($response, 'index.html', [
        /*'name' => $args['name']*/
    ])->withHeader("Permissions-Policy","interest-cohort=()");

});




$static = [
    'css'  => 'text/css',
    'js'   => 'text/javascript',
    'png'  => 'image/png',
    'gif'  => 'image/gif',
    'jpg'  => 'image/jpg',
    'jpeg' => 'image/jpg',
    'mp4'  => 'video/mp4'
];

function getStaticFile( swoole_http_request $request,  swoole_http_response $response, array $static ) : bool {
    $staticFile = __DIR__ . $request->server['request_uri'];
    if (! file_exists($staticFile)) {
        return false;
    }
    $type = pathinfo($staticFile, PATHINFO_EXTENSION);
    if (! isset($static[$type])) {
        return false;
    }
    $response->header('Content-Type', $static[$type]);
    $response->sendfile($staticFile);
    return true;
}


/**
 * Slim-Swoole stuff
 */

$bridgeManager = new BridgeManager($app);

$http = new swoole_http_server("0.0.0.0", 9501);

$http->set(['enable_coroutine' => true]);

$http->on("start", function (\swoole_http_server $server) {
    echo sprintf('Swoole http server is started at http://%s:%s', $server->host, $server->port), PHP_EOL;
});

$http->on("request", function (swoole_http_request $swooleRequest, swoole_http_response $swooleResponse) use ($bridgeManager,$static) {
    if (getStaticFile($swooleRequest, $swooleResponse, $static)) {
        return;
    }
    $bridgeManager->process($swooleRequest, $swooleResponse)->end();
});

$http->start();











function oui($query,$refresh){


    ## GET QUERY STRING




    # START A TIMER (USED TO CALCULATE EXECUTION TIME)
    $time = microtime();
    $time = explode(' ', $time);
    $time = $time[1] + $time[0];
    $start = $time;

    ## MEMORY FUNCTION
    $mem_peak = memory_get_peak_usage();

    ## FILENAME ##
    $filename = "oui.txt";


    $searchterm = $query;

    ## CHECK FOR MANUAL DATA REFRESH
    if ($refresh == "yes") {
        file_put_contents($filename, fopen("http://standards-oui.ieee.org/oui.txt", 'r'));
    }

    ## CHECK IF FILE ACTUALLY EXISTS IF NOT DOWNLOAD IT
    if (file_exists($filename)) {
        ## THE FILE EXISTS LETS DO NOTHING
    } else {
        file_put_contents($filename, fopen("http://standards-oui.ieee.org/oui.txt", 'r'));
    }

    ## CONVERT TO UPPER CASE TO EASE FORMATTING LATER
    $mac = strtoupper($query);

    ## CHECK WE GOT SOMETHING TO DO
    if ($searchterm == "") {
        echo "NO MAC DETECTED";
        die;
    }

    ## STRIP STRAY MAC FORMATTING CHARACTERS
    $mac = preg_replace("/[^A-Z0-9]/", "", $mac);

    $mac = str_replace(":", "", $mac);
    $mac = str_replace("-", "", $mac);
    $mac = str_replace(".", "", $mac);

    ## STRIP CHARACTERS OUTSIDE OF HEX RANGE
    $mac = str_replace("G", "", $mac);
    $mac = str_replace("H", "", $mac);
    $mac = str_replace("I", "", $mac);
    $mac = str_replace("J", "", $mac);
    $mac = str_replace("K", "", $mac);
    $mac = str_replace("L", "", $mac);
    $mac = str_replace("M", "", $mac);
    $mac = str_replace("N", "", $mac);
    $mac = str_replace("O", "", $mac);
    $mac = str_replace("P", "", $mac);
    $mac = str_replace("Q", "", $mac);
    $mac = str_replace("R", "", $mac);
    $mac = str_replace("S", "", $mac);
    $mac = str_replace("T", "", $mac);
    $mac = str_replace("U", "", $mac);
    $mac = str_replace("V", "", $mac);
    $mac = str_replace("W", "", $mac);
    $mac = str_replace("X", "", $mac);
    $mac = str_replace("Y", "", $mac);
    $mac = str_replace("Z", "", $mac);


    # LETS CHECK WE HAVE 6 CHARACTERS LEFT TO WORK WITH
    if (strlen($searchterm) < 6) {
        throw new Exception("TOO FEW CHARACTERS");
    }


    ### LETS SORT THE MAC OUT TO A GOOD FORMAT
    $searchterm = $mac;

    ## CUT MAC TO FIRST 6 DIGITS
    $mac = mb_substr($mac, 0, 6);

    ## ADJUST TO CORRECT FORMAT
    $searchterm = wordwrap($mac, 2, '-', true);

    ## OUI LOOKUP ##
    $handle = fopen("oui.txt", "r");

    $found = false;

    if ($handle) {
        $countline = 0;
        while (($buffer = fgets($handle, 4096)) !== false) {
            if (strpos($buffer, "$searchterm") !== false) {

                // FOUND A HEX MATCH
                $found = true;
                $result = $buffer;

            }
            $countline++;
        }
        fclose($handle);
    }

    if (!$found) {
        echo "NO MATCH FOUND";
        die;
    }

    // TIDY COMPANY NAME
    $company = mb_substr($result, 18);
    $company = str_replace("\n", "", $company);
    $company = str_replace("\r", "", $company);

    // STRA TO CONVERT RESULTS TO JSON
    $json_output = new \stdClass();
    $json_output->query = $query;
    $json_output->hex = mb_substr($result, 0, 8);
    $json_output->base16 = $mac;
    $json_output->company = $company;
    $json_output->data_source = date("F d Y H:i", filemtime($filename));

    // CALCULATE COMPUTATIONAL TIME TAKEN
    $time = microtime();
    $time = explode(' ', $time);
    $time = $time[1] + $time[0];
    $finish = $time;
    $total_time = round(($finish - $start), 4);

    // FINALIZE JSON RESPONSE
    $json_output->querytime = $total_time . "ms";
    $json_output->peakmemory = round($mem_peak / 1024) . "KB";


    return $json_output;

    $json = json_decode(json_encode($json_output), true);

    // SORT OUTPUT ORDERING

    // JSON ENCODE
    $sorted_response = json_encode($json, JSON_PRETTY_PRINT);

    // OUTPUT JSON
    //header('Content-Type: application/json');
    return $sorted_response;
}












