<?php


class ArgumentParser
{
    public bool $help = False;
    public string $directory = '.';
    public bool $recursive = false;
    public string $parse_script = 'parse.php';
    public string $int_script = 'interpret.py';
    public bool $parse_only = false;
    public bool $int_only = false;
    public string $jexampath = '/pub/courses/ipp/jexamxml';
    public bool $noclean = false;

}

class TestCase
{
    public bool $src = False;
    public bool $in = False;
    public bool $out = False;
    public bool $rc = False;
    public string $path = '';
    public string $name = '';

    public ?TestResult $result = null;

    public function __construct()
    {
        $this->result = new TestResult();
    }

    public function prepTest()
    {
        if (!$this->src)
            fwrite(STDERR, 'Testcase: ' . $this->name . ", has no source file and the test will not be performed\n");
        if (!$this->in)
            file_put_contents($this->path . '.in', '');
        if (!$this->out)
            file_put_contents($this->path . '.out', '');
        if (!$this->rc)
            file_put_contents($this->path . '.rc', '0');
    }

    public function doTest($args)
    {
        $this->result->test_name = $this->name;
        $this->result->test_folder = $this->path;
        if ($args->parse_only)
            $result = $this->doParse($args);
        elseif ($args->int_only)
            $result = $this->doInterpret($args);
        else {
            $this->doParse($args);
            $result = $this->doInterpret($args);
        }
        if (!$args->noclean)
            $this->cleanTmpFiles();
        return $result;
    }

    private function doParse($args)
    {
        $this->getfFiles();
        $exec_parser = 'php8.1 ' . $args->parse_script . ' < ' . $this->path . '.src > ' . $this->result->out . ' 2>' . $this->result->stderr;
        exec($exec_parser, $output, $this->result->exit);
        if ($this->result->exit == $this->result->e_exit)
            $this->result->state = 1;
        else
            $this->result->state = -1;

        $this->result->stderr = file_get_contents($this->path . '.stderr.tmp');

        if ($this->result->exit == $this->result->e_exit and $this->result->exit == 0) {
            $exec_jexamxml = 'java -jar ' . $args->jexampath . DIRECTORY_SEPARATOR . 'jexamxml.jar ' . $this->result->out . ' ' . $this->result->e_out . ' ' . $this->result->diff_out . ' ' . $args->jexampath . DIRECTORY_SEPARATOR . 'options';
            exec($exec_jexamxml, $output, $exit);
            if ($exit == 0)
                $this->result->diff = 1;
            elseif ($exit != 0) {
                $this->result->state = -1;
                $this->result->diff = 0;
            }
        }

        return $this->result;
    }

    private function doInterpret($args)
    {
        if ($args->int_only)
            $source = $this->path . '.src';
        else
            $source = $this->path . '.out.tmp';
        $this->getfFiles();
        $exec_int = 'python3.8 ' . $args->int_script . ' --source ' . $source . ' --input ' . $this->path . '.in > ' . $this->result->out . '.int 2> ' . $this->result->stderr;
        exec($exec_int, $output, $this->result->exit);
        if ($this->result->exit == $this->result->e_exit)
            $this->result->state = 1;
        else
            $this->result->state = -1;

        $this->result->stderr = file_get_contents($this->path . '.stderr.tmp');

        if ($this->result->exit == $this->result->e_exit and $this->result->exit == 0) {
            $exec_diff = 'diff -u ' . $this->result->out . '.int ' . $this->result->e_out;
            exec($exec_diff, $output, $exit);
            if ($exit == 0)
                $this->result->diff = 1;
            elseif ($exit != 0) {
                $this->result->state = -1;
                $this->result->diff = 0;
                $this->result->diff_out = $this->getDiff($output);
            }
        }
        return $this->result;
    }

    private function getDiff($diff)
    {
        unset($diff[0]);
        unset($diff[1]);
        foreach ($diff as $line => $val) {
            if ($val == '\\ No newline at end of file')
                unset($diff[$line]);
        }
        return implode('<br>', $diff);
    }

    private function getfFiles()
    {
        $this->result->stderr = $this->path . '.stderr.tmp';
        $this->result->out = $this->path . '.out.tmp';
        $this->result->e_out = $this->path . '.out';
        $this->result->e_exit = (int)trim(file_get_contents($this->path . '.rc'));
    }

    private function cleanTmpFiles()
    {
        if (file_exists($this->path . '.stderr.tmp'))
            unlink($this->path . '.stderr.tmp');
        if (file_exists($this->path . '.out.tmp'))
            unlink($this->path . '.out.tmp');
        if (file_exists($this->path . '.out.tmp.int'))
            unlink($this->path . '.out.tmp.int');
        if (file_exists($this->path . '.diff'))
            unlink($this->path . '.diff');
    }
}

class TestResult
{
    public string $test_name = '';
    public string $test_folder = '';
    public string $stderr = '';
    public string $e_out = '';
    public string $out = '';
    public int $e_exit = -1;
    public int $exit = -1;
    public int $state = 0;

    public string $diff_out = '';
    public int $diff = -1;

}

