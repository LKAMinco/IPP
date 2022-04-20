<?php

require_once('test_class.php');
require_once('html_generator.php');

function writeErr($code, $errMes)
{
    fwrite(STDERR, $errMes . "\n");
    exit($code);
}

function checkFilePath($path)
{
    if (!file_exists($path)) {
        fwrite(STDERR, "Path does not exist\n");
        exit(41);
    }
}

function setPath($path)
{
    $path = realpath($path);
    checkFilePath($path);
    return $path;
}

function parseArgs()
{
    $args = new ArgumentParser();
    $optional_arg = getopt('', ['help', 'directory:', 'recursive', 'parse-script:', 'int-script:', 'parse-only', 'int-only', 'jexampath:', 'noclean']);
    if (key_exists('help', $optional_arg)) {
        if (count($optional_arg) > 1)
            writeErr(10, 'Can not combine --help with other arguments');
        else
            $args->help = True;
    }
    if (key_exists('directory', $optional_arg))
        $args->directory = setPath($optional_arg['directory']);
    if (key_exists('recursive', $optional_arg))
        $args->recursive = True;
    if (key_exists('parse-script', $optional_arg))
        $args->parse_script = setPath($optional_arg['parse-script']);
    if (key_exists('int-script', $optional_arg))
        $args->int_script = setPath($optional_arg['int-script']);
    if (key_exists('parse-only', $optional_arg))
        $args->parse_only = True;
    if (key_exists('int-only', $optional_arg))
        $args->int_only = True;
    if (key_exists('jexampath', $optional_arg))
        $args->jexampath = setPath($optional_arg['jexampath']);
    if (key_exists('noclean', $optional_arg))
        $args->noclean = True;
    #checks whether there is no conflict between arguments
    if ($args->parse_only and $args->int_only)
        writeErr(10, 'Can not use --parse-only and --int-only at the same time');
    if ($args->parse_only and key_exists('int-script', $optional_arg))
        writeErr(10, 'Can not use --parse-only and --int-script at the same time');
    if ($args->int_only and key_exists('parse-script', $optional_arg))
        writeErr(10, 'Can not use --int-only and --parse-script at the same time');
    return $args;
}

#function returns all directories with tests
function loadDirectories($path, $recursive)
{
    $folders = [];
    $files_in_dir = scandir($path); #loads all files in directory
    foreach ($files_in_dir as $file) {
        if (str_contains($file, '.') and $file !== '..')
            continue;
        #better to use DIRECTORY_SEPARATOR then just '/' because on windows separator is '\' and on linux is '/'
        $path_to_file = $path . DIRECTORY_SEPARATOR . $file;
        if (is_dir($path_to_file))
            if ($recursive and $file !== '..' and $file !== '.')
                array_push($folders, ...loadDirectories($path_to_file, $recursive)); #recursive call for subfolders
            elseif ($file === '..')
                $folders[] = pathinfo($path_to_file);
    }
    return $folders;
}

function loadTests($args)
{
    $folders = loadDirectories($args->directory, $args->recursive);
    $all_files = [];
    $tests = [];
    foreach ($folders as $folder) {
        $files_in_folder = scandir($folder['dirname']);
        foreach ($files_in_folder as $file) {
            $path_to_file = $folder['dirname'] . DIRECTORY_SEPARATOR . $file;
            $file_info = pathinfo($path_to_file);
            if (!array_key_exists('extension', $file_info))
                continue;
            if (!in_array($file_info['extension'], ['src', 'in', 'out', 'rc']))
                continue;
            else {
                $test_name = $folder['dirname'] . DIRECTORY_SEPARATOR . $file_info['filename'];
                if (!key_exists($file_info['filename'], $tests))
                    $test = new TestCase();
            }
            if ($file_info['extension'] == 'src')
                $test->src = True;
            elseif ($file_info['extension'] == 'in')
                $test->in = True;
            elseif ($file_info['extension'] == 'out')
                $test->out = True;
            elseif ($file_info['extension'] == 'rc')
                $test->rc = True;
            $test->path = $test_name;
            $test->name = $file_info['filename'];
            $tests[$file_info['filename']] = $test;
        }
    }
    return $tests;
}

$args = parseArgs();

if ($args->help) {
    echo("Usage: php parse.php [--help] [--directory PATH] [--recursive] [--parse-script FILE] [--int-script FILE] [--parse-only] [--int-only] [--jexampath PATH] [--noclean]");
    echo("\n\noptions:\n");
    echo("  --help                  show this help message and exit\n");
    echo("  --directory PATH        loads test cases from \n");
    echo("  --recursive             loads tests from all subfolders\n");
    echo("  --parse-script FILE     parser FILE\n");
    echo("  --int-script FILE       interpret FILE\n");
    echo("  --parse-only            only parser tests are executed\n");
    echo("  --int-only              only interpret tests are executed\n");
    echo("  --jexampath PATH        PATH to the file containing jexamxml.jar\n");
    echo("  --noclean               keep temporary files after test\n");
    exit(0);
}

$tests = [];
$tests = loadTests($args);
ksort($tests);
$results = [];
$passed = 0;
$failed = 0;
foreach ($tests as $test) {
    $test->prepTest();
    if (!$test->src)
        continue;
    $result = new TestResult();
    $result = $test->doTest($args);
    $results[$test->name] = $result;
    if ($result->state == 1)
        $passed++;
    elseif ($result->state == -1)
        $failed++;
}

$page = new ResultsPage($passed, $failed, $args);
ksort($results);
foreach ($results as $result) {
    if ($result->state == 1)
        $page->makePassed($result->test_folder, $result->test_name);
    elseif ($result->state == -1) {
        $codes['e_exit'] = $result->e_exit;
        $codes['exit'] = $result->exit;
        $text['stderr'] = $result->stderr;
        if ($result->diff == 0) {
            $text['diff'] = $result->diff_out;
        }
        $page->makeFailed($result->test_folder, $result->test_name, $codes, $text);
    }
}
$page->makeEnd();
echo('');
