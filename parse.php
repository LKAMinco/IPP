<?php
/************************
 * Title: Projekt - 1. úloha v PHP 8.1
 * Author: Milan Hrabovský
 * Login: xhrabo15
 * Subject: IPP
 * Files: parse.php
 ************************/

//chceck whether there are no more arguments
if($argc > 2) {
    fwrite(STDERR, "Invalind number of argumetns\n");
    exit(1);
}
//prints help
if($argc > 1 )
    if ($argv[1] == "--help") {
        echo ("Script parse.php loads IPPcode22 source code from standard input, checks lexical and syntactic rules and prints XML representation of program to standard output.\n");
        echo ("\tusage: php parse.php [--help]\n");
        echo ("\t\t--help` prints help to standard output.");
        echo ("napoveda");
        exit(0);
    }
else {
    fwrite(STDERR, "Invalind agrument\n");  //return 1 if there is different argument[1] then --help
    exit(1);
}
//function to handle errors
function writeErr($code, $lineNum, $errMes) {
    fwrite(STDERR, "Line $lineNum - $errMes \n");
    exit($code);
}
//check whether the variable have valid characters in name
function checkVar($lineStr, $lineNum) {
    if(preg_match('/^[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$/', $lineStr[1]) !== 1)
        writeErr(23, $lineNum, "Wrong variable name");
}
//check whether the constant have right value
function checkConst($lineStr, $lineNum) {
    if($lineStr[0] == 'int')
        if(preg_match('/^-[0-9]+|[0-9]+$/', $lineStr[1]) !== 1)
            writeErr(23, $lineNum, "Wrong integer value");
    if($lineStr[0] == 'bool')
        if($lineStr[1] != "true" && $lineStr[1] != "false")
            writeErr(23, $lineNum, "Wrong boolean value");
    if($lineStr[0] == 'string'){
        if(preg_match_all('/\\\\/', $lineStr[1]) !== preg_match_all('/\\\\[0-9]{3}/', $lineStr[1]))
            writeErr(23, $lineNum, "Wrong string format");
    }
}

function checkArg($lineStr, $lineNum, $type, $order) {
    $lineStr = preg_split('/\@/', $lineStr);
    if($lineStr[0] == "LF" || $lineStr[0] == "GF" || $lineStr[0] == "TF"){
        checkVar($lineStr, $lineNum);
        $lineStr[1] = preg_replace('/\&/', '&amp;', $lineStr[1]);
        $lineStr[1] = preg_replace('/\</', '&lt;', $lineStr[1]);
        $lineStr[1] = preg_replace('/\>/', '&gt;', $lineStr[1]);
        writeArg($order, "var", "$lineStr[0]@$lineStr[1]");
    } elseif($lineStr[0] == "int" || $lineStr[0] == "string" || $lineStr[0] == "bool"){
        if($type == "var")
            writeErr(23, $lineNum,"Wrong type");
        checkConst($lineStr, $lineNum);
        $lineStr[1] = preg_replace('/\&/', '&amp;', $lineStr[1]);
        $lineStr[1] = preg_replace('/\</', '&lt;', $lineStr[1]);
        $lineStr[1] = preg_replace('/\>/', '&gt;', $lineStr[1]);
        writeArg($order, $lineStr[0], $lineStr[1]);
    } elseif($lineStr[0] == "nil"){
        if($type == "var" || $type == "nil")
            writeErr(23, $lineNum,"Wrong variable");
        if($lineStr[1] != "nil")
            writeErr(23, $lineNum,"Wrong nil value");
        writeArg($order, $lineStr[0], $lineStr[1]);
    } else
        writeErr(23, $lineNum,"Wrong type or frame");
}

function checkLabel($lineStr, $lineNum) {
    if(preg_match('/^[a-zA-Z\_\-\$\&\%\*\!\?][a-zA-Z0-9\_\-\$\&\%\*\!\?]*$/', $lineStr) !== 1)
        writeErr(23, $lineNum, "Wrong label name");
}
//function which checks whether the type is valid
function checkType($lineStr, $lineNum) {
    if(strcmp($lineStr,"int") && strcasecmp($lineStr,"string") && strcasecmp($lineStr,"bool")) {
        writeErr(23, $lineNum, "Wrong type");
    }
}
//function to check whether the instruction have right number of arguments
function checkNumOfArgs($lineStr, $lineNum, $count){
    if(count($lineStr) != $count) {
        writeErr(23, $lineNum, "Wrong number of arguments");
    }
}
//function to handle print of head of instruction to xml
function writeStartFunc($code){
    static $order = 1;
    $code = strtoupper($code);
    echo ("\t<instruction order=\"$order\" opcode=\"$code\">\n");
    $order++;
}
//function to handle print of agruments to xml
function writeArg($order, $type, $value) {
    echo ("\t\t<arg$order type=\"$type\">$value</arg$order>\n");
}

function wrinteEndFunc(){
    echo ("\t</instruction>\n");
}

function doItShorter($lineStr, $lineNum) {
    checkNumOfArgs($lineStr, $lineNum, 4);
    writeStartFunc($lineStr[0]);
    checkArg($lineStr[1], $lineNum, "var", 1);
    checkArg($lineStr[2], $lineNum, "", 2);
    checkArg($lineStr[3], $lineNum, "", 3);
    wrinteEndFunc();
}
//this fucntion handle instruction, check number of agrument, and validity of arguments, depentding on type of instruction, it also formate instructions in xml
function instructionCheck($lineStr, $lineNum){
    //⟨var⟩ ⟨symb⟩ - move, int2char, strlen, type
    if(!strcasecmp($lineStr[0],"move") || !strcasecmp($lineStr[0],"int2char") || !strcasecmp($lineStr[0],"strlen") || !strcasecmp($lineStr[0],"type")  || !strcasecmp($lineStr[0],"not")) {
        checkNumOfArgs($lineStr, $lineNum, 3);
        writeStartFunc($lineStr[0]);
        checkArg($lineStr[1], $lineNum, "var", 1);
        checkArg($lineStr[2], $lineNum, "", 2);
        wrinteEndFunc();
        //⟨var⟩ - defvar, pops
    } elseif(!strcasecmp($lineStr[0],"defvar") || !strcasecmp($lineStr[0],"pops")) {
        checkNumOfArgs($lineStr, $lineNum, 2);
        writeStartFunc($lineStr[0]);
        checkArg($lineStr[1], $lineNum, "var", 1);
        wrinteEndFunc();
        //⟨label⟩ - call, label, jump,
    } elseif(!strcasecmp($lineStr[0],"call") || !strcasecmp($lineStr[0],"label") || !strcasecmp($lineStr[0],"jump")) {
        checkNumOfArgs($lineStr, $lineNum, 2);
        writeStartFunc($lineStr[0]);
        checkLabel($lineStr[1], $lineNum);
        writeArg(1, "label", $lineStr[1]);
        wrinteEndFunc();
        //⟨symb⟩ - pushs, write, exit, dprint
    } elseif(!strcasecmp($lineStr[0],"pushs") || !strcasecmp($lineStr[0],"write") || !strcasecmp($lineStr[0],"exit") || !strcasecmp($lineStr[0],"dprint")) {
        checkNumOfArgs($lineStr, $lineNum, 2);
        writeStartFunc($lineStr[0]);
        checkArg($lineStr[1], $lineNum, "", 1);
        wrinteEndFunc();
        //⟨var⟩ ⟨symb1⟩ ⟨symb2⟩ - add, sub, mul, idiv, lt, gt, eq, and, or, stri2int, concat, getchar, setchar
    } elseif(!strcasecmp($lineStr[0],"add") || !strcasecmp($lineStr[0],"sub") || !strcasecmp($lineStr[0],"mul") || !strcasecmp($lineStr[0],"idiv")) {
        doItShorter($lineStr, $lineNum);
    } elseif(!strcasecmp($lineStr[0],"lt") || !strcasecmp($lineStr[0],"gt") || !strcasecmp($lineStr[0],"eq")) {
        doItShorter($lineStr, $lineNum);
    } elseif(!strcasecmp($lineStr[0],"and") || !strcasecmp($lineStr[0],"or")) {
        doItShorter($lineStr, $lineNum);
    } elseif(!strcasecmp($lineStr[0],"stri2int") || !strcasecmp($lineStr[0],"concat") || !strcasecmp($lineStr[0],"getchar") || !strcasecmp($lineStr[0],"setchar")) {
        doItShorter($lineStr, $lineNum);
        //⟨var⟩ ⟨type⟩ - read
    }  elseif(!strcasecmp($lineStr[0],"read")) {
        checkNumOfArgs($lineStr, $lineNum, 3);
        writeStartFunc($lineStr[0]);
        checkArg($lineStr[1], $lineNum, "var", 1);
        checkType($lineStr[2], $lineNum);
        writeArg(2, "type", $lineStr[2]);
        wrinteEndFunc();
        //⟨label⟩ ⟨symb1⟩ ⟨symb2⟩ - jumpifeq, jumpifneq
    } elseif(!strcasecmp($lineStr[0],"jumpifeq") || !strcasecmp($lineStr[0],"jumpifneq")) {
        checkNumOfArgs($lineStr, $lineNum, 4);
        writeStartFunc($lineStr[0]);
        checkLabel($lineStr[1], $lineNum);
        writeArg(1, "label", $lineStr[1]);
        checkArg($lineStr[2], $lineNum, "", 2);
        checkArg($lineStr[3], $lineNum, "", 3);
        wrinteEndFunc();
        //--- - createframe, pushframe, popframe, return, break
    } elseif(!strcasecmp($lineStr[0],"createframe") || !strcasecmp($lineStr[0],"pushframe") || !strcasecmp($lineStr[0],"popframe") || !strcasecmp($lineStr[0],"return") || !strcasecmp($lineStr[0],"break")) {
        checkNumOfArgs($lineStr, $lineNum, 1);
        writeStartFunc($lineStr[0]);
        wrinteEndFunc();
    } else {
        writeErr(22, $lineNum, "Wrong instruction");
    }
}

while($line = fgets(STDIN)) { //loop throught input from stdin
    static $head = false;
    static $lineNum = 0;
    $order = 1;
    $lineNum++;
    $line = preg_replace('/^\s+|\s+$/', '', $line); //remove all whitespace on start and end of the line
    $line = preg_replace('/\s*\#.*$/', '', $line); //remove comments
    if($line == '') //remove empty lines
        continue;
    $lineStr = preg_split('/\s+/', $line); //divide line into stings into array
    if(!$head) //chceck if the code contains just one head
        if($lineStr[0] != '' && strcasecmp($lineStr[0],'.IPPcode22')) {
            writeErr(21, $lineNum, "Missing head");
        } else { // print head
            checkNumOfArgs($lineStr, $lineNum, 1);
            echo("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
            echo("<program language=\"IPPcode22\">\n");
            $head = true;
            continue;
        }
    instructionCheck($lineStr, $lineNum); //call for handle other instruction
}
echo("</program>");
exit(0);