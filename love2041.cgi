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
	
	if(!param('Next set of students') && param('my preference user') || param('Next sets of matched student')) {
		my $preference = param('preference');
		my $userlooking = param('user');
		@matched_stu = @{choose_matched($userlooking)};
		print matched_profile(\@matched_stu);
	}
	
	if(!param() || defined param('logout')){
		$login = param('logout') || 0;
		if($login == 0){
			print login_page();
		}
	}
	if($ENV{'QUERY_STRING'} =~ /\w+/){
		my $q = $ENV{'QUERY_STRING'};
		print detail($q);
	}
	if(param('set') && param('string_user') eq "" && !param('my preference user')){
		print set10();
	}
	if(param('username') && param('password') && !param('set')){
		$authentication = 0;
		$authenticate_user = 0;
		$username = param('username');
		$password = param('password');
		authen_page(\$authentication,\$authenticate_user,\$username,\$password);
		if($authentication){
			print p(
					{
						-class=>'Tip'
					},
					"Hi, ", param('username'), " Welcome!"
				), "\n";
			print set10($username);
			$login += 1;
			print start_form(-method=>'post'),
			hidden('logout',$login-1),
			submit("logout"),
			end_form;
		}
		
	}
	
	if(param('string_user')){
		
		my $search_user = param('string_user');
		 $search_user =~ s/\W//g;
		my @users;
		my @students = glob("$students_dir/*");
		foreach my $student(@students){
			my (my $dot, my $dir,my $user) = split /\//,$student;
			
			if ($user =~ m/($search_user)/) {
				push(@users, $user);
			}
		}
		
		print search_user_page(\@users,$search_user);
	}
	
	print page_footer();
	exit 0;
}

sub choose_matched{
	$userlook = shift @_;
	open USERFILE, "< $students_dir/$userlook/preferences.txt" or die;
	my $line;
	
	while($line = <USERFILE>){
		chomp $line;
		
		if ($line eq "gender:"){
			
			if($line = <USERFILE>){
				chomp $line;
				if($line =~ /^\s+/){
					$line =~ s/^\s+//;
					$gender = $line;
				}
			}
		}elsif ($line eq "age:"){
			
			while($line = <USERFILE>){
				chomp $line;
				if($line =~ /min:/){
					if($line = <USERFILE>){
						chomp $line;
						if($line =~ /^\s+\d+$/){
							$line =~ s/^\s+//;
							$min_age = $line;
							$min_date_birth = 2014 - $min_age;
							$min_date_birth_extend = 2014 - $min_age + 2;
						}
					}
				}else{
					if(($line =~ /max:/) && ($line = <USERFILE>)){
						chomp $line;
						if($line =~ /^\s+\d+$/){
							$line =~ s/^\s+//;
							$max_age = $line;
							$max_date_birth = 2014 - $max_age;
							$max_date_birth_extend = 2014 - $max_age - 2;
						}
					}
					last;
				}
			}
			
		}elsif($line eq "weight:"){
			
			while($line = <USERFILE>){
				chomp $line;
				
				if($line =~ /min:/){
					if($line = <USERFILE>){
						chomp $line;
						if($line =~ /^\s+\d+kg$/){
							$line =~ s/^\s+//;
							$line =~ s/kg//;
							$min_weight = $line;
							$min_weight_extend = $min_weight - 2;
						}
					}
				}else{
					if(($line =~ /max:/) && ($line = <USERFILE>)){
						chomp $line;
						
						if($line =~ /^\s+\d+$/){
							$line =~ s/^\s+//;
							$line =~ s/kg//;
							$max_weight = $line;
							$max_weight_extend = $max_weight + 2;
						}
					}
					last;
				}
			}
			
		}else{
			
		}
		#more thing here.
		
	}
	close USERFILE;
	#open evey user's profile, caculate the score: gender, not match,next; 2014-min+2 <= age <= 2014-max-2, match 20, not match -50;
	#weight
	my @students = glob("$students_dir/*");
	foreach my $stu_path(@students){
		$stu_path =~ s/\.\/students\///;
		push(@student_name, $stu_path);
	}
	
	foreach my $student (@student_name){
		my $stu_profile = "$students_dir/$student/profile.txt";
		open my $f, "$stu_profile" or die "can not open $profile_filename: $!";
		
		while($l = <$f>){
			chomp $l;
			if($l =~ /gender:/){
				while($l = <$f>){
					chomp $l;
					$l =~ s/^\s*//;
					if($l eq $gender){
						$score{$student} += 0;
					}else{
						$score{$student} -= 1000;
					}
					last;
				}
				print $student,"'s gender score is ",$score{$student},br;
			}
			if($l eq "birthdate:"){
				while($l = <$f>){
					chomp $l;
					$l =~ s/^\s*//;
					if($l =~ /(\d{4})\/?/){
						$birth_year = $1;
					}
					if($birth_year <= $min_date_birth && $birth_year >= $max_date_birth){
						
						$score{$student} += 100;
					}elsif($birth_year <= $min_date_birth_extend && $birth_year >= $max_date_birth_extend){
						$score{$student} += 50;
					}else{
						$score{$student} -= 100;
					}
					last;
				}
				print $student,"'s age score is ",$score{$student},br;
			}
			if($l eq "weight:"){
				while($l = <$f>){
					chomp $l;
					$l =~ s/^\s*//;
					if($l =~ /(\d+)kg/){
						$w = $1;
					}
					if($w >= $min_weight && $w <= $max_weight){
						$score{$student} += 50;
						
					}elsif($w >= $min_weight_extend && $w <= $max_weight_extend){
						$score{$student} += 20;
						
					}else{
						$score{$student} -= 20;
					}
					last;
				}
				print $student,"'s weight score is ",$score{$student},br();
			}
			
			
			
			
			
						
		}
		close $f;
	}
	@matched_student = sort{$score{$b} <=> $score{$a}} keys %score;
	return \@matched_student;
}

# showing matching data according my preference in the record.
sub matched_profile{
	my @matched_profile = @{$_[0]};
	print @matched_profile;
	
	my $matched_sets = param('matched_sets') || 0;
	print "matched sets is ",$matched_sets;
	$matched_sets = min(max($matched_sets, 0), $#matched_profile);
	param('matched_sets', $matched_sets + 10);
	foreach my $h ($matched_sets..$matched_sets+9){
		push (@new_matched_set, $matched_profile[$h]);
	}
	
	foreach my $j ($matched_sets..$matched_sets+9){
		if($matched_profile[$j]){
			my $student_to_show  = $matched_profile[$j];
			print $student_to_show,br;
			my $profile_filename = "$students_dir/$student_to_show/profile.txt";
			open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
			print $profile_filename,br;
			my $profile = ""; my @lines = <$p>;
			foreach my $i (0..$#lines){
				my $line = $lines[$i];
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
			$matched_mini_profile{$student_to_show} = $profile;
		}
	}
	return p(
			{
				-class=>'Tip'
			},
			"Matched profile based on your Preference."
		),"\n",
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
							$matched_mini_profile{$_}
						)
						
					)
			   )
			} @new_matched_set
		),
		hidden('user',param('user')),
		hidden('matched_sets', $matched_sets + 10),"\n",
		submit('Next sets of matched student'),"\n",
		end_form, "\n",
		p, "\n";
}

sub search_user_page{
	my @students = @{$_[0]};
	my $userstring = $_[1];
	my $sets = param('sets') || 0;
	$sets = min(max($sets, 0), $#students);
	param('sets', $sets + 10);
	
	foreach my $j ($sets..$sets+9){
		if($students[$j]){
			my $student_to_show  = $students[$j];
			
			my $profile_filename = "$students_dir/$student_to_show/profile.txt";
			open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
			my $profile = ""; my @lines = <$p>;
			foreach my $i (0..$#lines){
				my $line = $lines[$i];
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
			$mini_profile{$student_to_show} = $profile;
		}
	}
	return p(
			{
				-class=>'Tip'
			},
			"Here are your search results."
		),"\n",
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
		hidden('string_user',$userstring),
		hidden('sets', $sets + 10),"\n",
		submit('Next set of search results'),"\n",
		end_form, "\n",
		p, "\n";
}

sub authen_page{
	my (my $authentication, my $authenticate_user,my $username, my $password) = @_;
	my @students = glob("$students_dir/*");
	foreach my $student(@students){
		my ($dot,$dir,my $user) = split /\//,$student;
		if ($$username eq $user) {
			$$authenticate_user = 1;
			open F,"< $student/profile.txt" or die;
			while(my $line = <F>){
				chomp $line;
				if($line eq "password:"){
					while($line = <F>){
						chomp $line;
						if($line =~ /^\s/){
							$line =~ s/^\s*//;
							if($line eq $$password){
								$$authentication = 1;
							}
						}
					}
					if($$authentication == 0){
						print
						start_html,
						p({-class=>'Tip'},
						"Wrong password!"),
						,
						end_html;
					}
				}
			}
			close F;
		}
	}
	if($$authenticate_user == 0){print
						start_html,
						p({-class=>'Tip'},
						"User doesn't exist!"),
						end_html;}
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
		p,"\n",
		"New User", br, "\n",
		submit(-value=>'register'),"\n",
		
		end_form;
		print "<br>\n";
		p, "\n";
}

sub set10 {
	my $user = shift @_;
	my $set = param('set') || 0;
	my @students = glob("$students_dir/*");
	$set = min(max($set, 0), $#students);
	param('set', $set + 10);
	foreach my $stu_path(@students){
		$stu_path =~ s/\.\/students\///;
		push(@student_name, $stu_path);
	}
	foreach $j ($set..$set+9){
		my $student_to_show  = $student_name[$j];
		my $profile_filename = "$students_dir/$student_to_show/profile.txt";
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
		$mini_profile{$student_name[$j]} = $profile;
	}
	return p(
			{
				-class=>'Tip'
			},
			"Eveyday, find your loved one."
		),"\n",
		start_form(-class=>'Tip',
			-method=>'post',
			-action=>''
		), "\n",
		
		# search usename interface.
		p("Searching, if you know someone's username"),
		textfield(-name=>'string_user', -size=>'15',-maxlength=>'20'),"\n",
		submit("Search"),"\n",
		
		#search user based on preference
		p,
		p("If you like to searching user based on your preference..."),
		hidden('user',$user),
		hidden('preference',1),
		submit("my preference user"),
		
		p,
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
	
	$n = shift @_;
	my @students = glob("$students_dir/*");
	my $student_to_show  = $n;
	my $profile_filename = "$students_dir/$student_to_show/profile.txt";
	open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
	
	#delete private parts of the profile.
	$profile = "";
	@lines = <$p>;
	foreach $i (0..$#lines){
		$line = $lines[$i];
		chomp $line;
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
