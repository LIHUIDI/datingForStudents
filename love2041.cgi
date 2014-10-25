#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2013
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/LOVE2041/

use CGI qw/:all/;
use CGI qw/:standard :html3/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
warningsToBrowser(1);

# some globals used through the script
$debug = 1;
$students_dir = "./students";

#here is the stylesheet
$newStyle=<<END;
<!--
	Pre.Tip {
			font-family: "Times New Roman";
			font-size: 20px;
			margin-right: 50pt;
			margin-left: 50pt;
			color: black;
   }
	Pre.Tip2 {
		font-family: "Times New Roman";
		font-size: 20px;
		margin-right: 50pt;
		margin-left: 40pt;
		color: red;
  }
	Form.Tip {
			font-family: "Times New Roman";
			font-size: 20px;
			margin-right: 50pt;
			margin-left: 50pt;
			
	  }
	P.Tip {
			font-family: "Times New Roman";
			font-size: 30px;
			margin-right: 50pt;
			margin-left: 50pt;
			color: red;
   }
   P.Alert {
	font-size: 30pt;
    font-family: sans-serif;
    color: BLACK;
   }
   -->
END

print main_control();

sub main_control(){
	# print start of HTML ASAP to assist debugging if there is an error in the script
	print page_header();
	if(!param()){
		print login_page();
	}
	if($ENV{'QUERY_STRING'} =~ /\d+/){
		my $q = $ENV{'QUERY_STRING'};
		print detail($q);
	}
	if(param('set')){
		print set10();
	}
	if(param('username') && param('password') && !param('set')){ 
		print p(
					{
						-class=>'Tip'
					},
					"Hi, ", param('username'), " Welcome!"
				),
			br, "\n";
		print set10();
	}

	print page_footer();
	exit 0;
}
	
sub login_page{
	return p,
		start_form(-class=>'Tip',
		-method=>'post',
		-action=>''
		), "\n",
		
		"Username: ",
		textfield(-name=>'username',-size=>'15', -maxlength=>40), br, "\n",
		
		"Password: ",
		password_field(-name=>'password',-size=>'15'), br, "\n",
		
		submit(-value=>'login'), br, "\n",
		
		"New User", br, "\n",
		submit(-value=>'register'),"\n",
		
		end_form;
		print "<br>\n";
		p, "\n";
}

sub set10 {
	my $set = param('set') || 0;
	my @students = glob("$students_dir/*");
	$set = min(max($set, 0), $#students);
	
	param('set', $set + 10);
	
	foreach $j ($set..$set+9){
		my $student_to_show  = $students[$j];
		my $profile_filename = "$student_to_show/profile.txt";
		open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
	
		$profile = ""; @lines = <$p>;
		foreach $i (0..$#lines){
			$line = $lines[$i];
			chomp $line;		
			if($lines[$i] =~ /(\bpassword\b|\bname\b|\bemail\b|\bfavourite_movies\b|\bfavourite_books\b|\bfavourite_bands\b|\bfavourite_TV_shows\b|\bfavourite_hobbies\b|\bhair_colour\b|\bdegree\b)/){
			
				while($lines[$i+1]){
					if($lines[$i+1] =~ /^[^\s]/){
						last;
					}else{				
						$lines[$i+1] =~ s/^.*$//;
					}
					$i = $i+1;
				}
				$lines[$i] =~ s/^.*$//; next;
			}
		
			if($line =~ /\bcourses\b/) {next;}
			if($line =~ /\b[A-Z]{4}\d{4}\b/) {next;}
			if($line eq ""){next;}
			$profile .= "$line\n";
		}
		close $p;
		$mini_profile{$j} = $profile;
	}
	return
	
		p(
			{
				-class=>'Tip'
			},
			"Eveyday, find your loved one."
		),
		start_form(-class=>'Tip',
			-method=>'post',
			-action=>''
		), "\n",
		
		table({-border=>"1", -width=>'100%'},
		map{
			Tr(
					td({-width=>'30%',-align=>'center',-bgcolor=>'FFFF99'},
						img(
							{
								-src=>'./image.cgi?'.$_, 
								-alt=>"student's profile image"
							}
						),
						a({href=>'./love2041.cgi?'.$_},"I want to see more"),
				
					),
					td({-width=>'50%',-align=>'left',-bgcolor=>'white'},
					
						pre(
							{
								-class=>'Tip'
							},
							$mini_profile{$_}
						)
						
					)
			   )
			} sort keys %mini_profile
		),
		
		hidden('set', $set + 10),"\n",
		submit('Next set of students'),"\n",
		end_form, "\n",
		p, "\n";
}

sub detail {
	
	#my $n = param('n') || 0;
	$n = shift @_;
	my @students = glob("$students_dir/*");
	#$n = min(max($n, 0), $#students);
	
	#param('n', $n + 1);
	
	my $student_to_show  = $students[$n];
	
	my $profile_filename = "$student_to_show/profile.txt";
	open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
	
	#delete private parts of the profile.
	$profile = "";
	@lines = <$p>;
	foreach $i (0..$#lines){
		$line = $lines[$i];
		chomp $line;
		#if($lines[$i] =~ /(\bpassword\b|\bname\b|\bemail\b)/){ $lines[$i] =~ s/^.*$//; $lines[$i+1] = s/^.*$//; next;}
		if($lines[$i] =~ /(\bpassword\b|\bname\b|\bemail\b)/){
		
			while($lines[$i+1]){
				if($lines[$i+1] =~ /^[^\s]/){
					last;
				}else{				
					$lines[$i+1] =~ s/^.*$//;
				}
				$i = $i+1;
			}
			$lines[$i] =~ s/^.*$//; next;
		}
		
		
		if($line =~ /\bcourses\b/) {next;}
		if($line =~ /\b[A-Z]{4}\d{4}\b/) {next;}
		if($line eq "1"){next;}
		if($line eq ""){next;}
		$profile .= "$line\n";
	}
	close $p;
	
	return 
		p(
			{
				-class=>'Tip'
			},
			"Look at my details..."
		),
		
		start_form(
			-class=>'Tip',
			-method=>'post',
			-action=>''
		), "\n",
		table({-border=>"1", -width=>'100%'},
			Tr(td({-width=>'20%',-align=>'center',-bgcolor=>'FFFF99'},
					img(
						{
							-src=>'./image.cgi?'.$n, 
							-alt=>"student's profile image"
						}
					)
				),
				td({-width=>'50%',-align=>'left',-bgcolor=>'white'},
					pre(
						{
							-class=>'Tip'
						},
						$profile
					)
				)
			)
		),
		end_form, "\n",
		p, "\n";
}

#
# HTML placed at header of every screen
#
sub page_header {
	return header,
   		start_html(
			"-title"=>"LOVE2041", 
			-bgcolor=>"#C0C0C0",
			-style=>{
				-src=>'',
				-code=>$newStyle
			}
		),
 		center(h1(i({-color=>'red'},"LOVE TODAY"))),"\n";
}

#
# HTML placed at bottom of every screen
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_footer {
	my $html = "";
	#here param()has no argument, it will list all the param received by the script.
	$html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
	#finish html doc.
	$html .= end_html;
	return $html;
}
