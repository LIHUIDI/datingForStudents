#!/usr/bin/perl -w
use CGI qw/:all/;
use CGI qw/:standard :html3/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
warningsToBrowser(1);

# some globals used through the script
$debug = 1;
$students_dir = "./students";

my $i = $ENV{'QUERY_STRING'};

my $student_to_show  = $i;

my $profile_imgname = "$students_dir/$student_to_show/profile.jpg";

open (IMAGE, "$profile_imgname");
$size = -s "$profile_imgname";
read IMAGE, $data, $size;
close(IMAGE);

print header(-type=>'image/jpg'),$data;
exit;