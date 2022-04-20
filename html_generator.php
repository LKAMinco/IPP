<?php

class ResultsPage
{
    public function __construct($passed, $failed, $args)
    {
        $this->makeHead();
        $this->makeStyle();
        $this->makeHeader($passed, $failed, $args);
    }

    public function makeHead()
    {
        echo('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>IPPcode22</title>
        <style>html {background: #2b2b2b;margin: 0;padding: 0;}
        body {box-sizing: border-box;font-family: "Nirmala UI", sans-serif;color: #bfbfbf;padding-left: 100px;padding-right: 100px;}
        h2 {margin: 5px;}h3 {margin: 5px;padding-bottom: 5px;}
        .passed {background: #008e3d;}.passed table {padding-left: 15px;padding-bottom: 5px;}.passed table tr th {text-align: left;}
        .failed {background: #a70000;}.failed table {padding-left: 15px;padding-bottom: 5px;}.failed table tr th {text-align: left;}</style></head>');
    }

    public function makeStyle()
    {
        echo('<style>html {background: #2b2b2b;margin: 0;padding: 0;}
        body {box-sizing: border-box;font-family: "Nirmala UI", sans-serif;color: #bfbfbf;padding-left: 100px;padding-right: 100px;}
        h2 {margin: 5px;}h3 {margin: 5px;padding-bottom: 5px;}
        .passed {background: #008e3d;}.passed table {padding-left: 15px;padding-bottom: 5px;}.passed table tr th {text-align: left;}
        .failed {background: #a70000;}.failed table {padding-left: 15px;padding-bottom: 5px;}.failed table tr th {text-align: left;vertical-align: text-top;}</style>');
    }

    public function makeHeader($passed, $failed, $args)
    {   #TODO vyriešit print test configuracie
        if ($passed + $failed != 0)
            $percent = $passed / ($passed + $failed) * 100;
        else
            $percent = 0;
        $percent = (int)$percent;
        $directory = $recursive = $parse_script = $int_script = $parse_only = $int_only = $jexampath = $noclean = '';
        if ($args->directory != '.')
            $directory = '<li>--directory <a>' . $args->directory . '</a></li>';
        if ($args->recursive)
            $recursive = '<li>--recursive</li>';
        if ($args->parse_script != 'parse.php')
            $parse_script = '<li>--parse-script <a>' . $args->parse_script . '</a></li>';
        if ($args->int_script != 'interpret.py')
            $int_script = '<li>--int-script <a>' . $args->int_script . '</a></li>';
        if ($args->parse_only)
            $parse_only = '<li>--parse-only</li>';
        if ($args->int_only)
            $int_only = '<li>--int-only</li>';
        if ($args->jexampath != '/pub/courses/ipp/jexamxml')
            $jexampath = '<li>--jexampath <a>' . $args->jexampath . '</a></li>';
        if ($args->noclean)
            $noclean = '<li>--noclean</li>';


        echo('<body><header><h1>IPP 2022 Test results</h1></header><section>
        <div><h2>Test configuration</h2><div><ul>' .
            $directory . $recursive . $parse_script . $int_script . $parse_only . $int_only . $jexampath . $noclean
            . '</ul></div></div>
        <div><h2>Overall rating - ' . $percent . '%</h2>
        <table><tr><td>Passed:</td><td>' . $passed . '</td></tr>
        <tr><td>Failed:</td><td>' . $failed . '</td></tr>
        <tr><td>All:</td><td>' . $passed + $failed . '</td></tr></table></div></section>
        <section><h1>Tests results</h1>');
    }

    public function makePassed($dir, $name)
    {
        echo('    <div class="passed"><h2>PASSED</h2><table>
        <tr><th>Directory:</th><td>' . $dir . '</td></tr>
        <tr><th>TestCase:</th><td>' . $name . '</td></tr></table></div>');
    }

    public function makeFailed($dir, $name, $codes, $text)
    {
        $e_exit = $exit = 0;
        $stderr = '';
        $diff = '';

        if (array_key_exists('e_exit', $codes))
            $e_exit = $codes['e_exit'];
        if (array_key_exists('exit', $codes))
            $exit = $codes['exit'];
        if (array_key_exists('stderr', $text))
            $stderr = $text['stderr'];
        if (array_key_exists('stderr', $text))
            $stderr = $text['stderr'];
        if (array_key_exists('diff', $text))
            $diff = '<tr><th>Different output</th><td>' . $text['diff'] . '</td></tr>';

        echo('<div class="failed"><h2>FAILED</h2><table>
        <tr><th>Directory: </th><td>' . $dir . '</td></tr>
        <tr><th>TestCase: </th><td>' . $name . '</td></tr>
        <tr><th>Expected exit: </th><td>' . $e_exit . '</td></tr>
        <tr><th>Current exit: </th><td>' . $exit . '</td></tr>
        <th>Stderr: </th><td>' . $stderr . '</td>
        ' . $diff . '
        </table></div>');
    }

    public function makeEnd()
    {
        echo('</section></body></html>');
    }
}