<?php
error_reporting(E_ALL);
$port = 9050;
$sock = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
socket_set_option($sock, SOL_SOCKET, SO_REUSEADDR, 1);
socket_bind($sock, 0, $port);
socket_listen($sock);

$clients = array($sock);
$auth_clients = array();
while (true) {

    $read = $clients;
    if (socket_select($read, $write = NULL, $except = NULL, 10) < 1)
        continue;

    if (in_array($sock, $read)) {
        $new_sock = socket_accept($sock);
        $clients[] = $new_sock;
        socket_write($new_sock, "This simple chat server. Type 'iam:username' for authorize!\n");
        echo "There are " . (count($clients) - 1) . " client(s) connected to the server\n";
        $key = array_search($sock, $read);
        unset($read[$key]);
    }

    foreach ($read as $read_sock) {
        $data = @socket_read($read_sock, 1024, PHP_NORMAL_READ);
        $key = array_search($read_sock, $clients);

        if ($data === false) {
            unset($clients[$key]);
            echo "Client disconnected.\n";
            continue;
        }

        $data = trim($data);

        if (empty($data)) {
            continue;
        }

        $auth_re = '/^iam\:(.+)$/i';
        if (preg_match($auth_re, $data, $matches)) {
            $auth_clients[$key] = $matches[1];
            echo "Socket: $key authed; Username: {$matches[1]}\n";
            $data = "New user ({$matches[1]}) input into chat. Hello {$matches[1]}!!!";
        } else {
            $username = isset($auth_clients[$key]) ? $auth_clients[$key] : 'Anon' . $key;
            $data = "[$username]: $data";
        }
        
        foreach ($clients as $send_sock) {
            if ($send_sock == $sock)
                continue;
            else
                socket_write($send_sock, $data . "\n");
        }

    }
}
socket_close($sock);
