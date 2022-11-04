#!/usr/bin/perl
use File::Basename;
use Cwd 'abs_path';
use MongoDB;
use POSIX qw( strftime );
use Time::HiRes qw( sleep );
use Digest::SHA qw( sha1_hex );
use Data::Dumper qw(Dumper);
use integer;
use Config::IniFiles;

my $file =  abs_path(__FILE__);
my $file_path = dirname($file);
my $base_path = dirname(dirname(dirname($file_path)));
my $local_config_file = abs_path("${base_path}/local_config.ini");
my $cfg = Config::IniFiles->new( -file => $local_config_file );

#print "file: ${file}\n";
#print "file dir: ${file_path}\n";
#print "base proyect: ${base_path}\n";

print $local_config_file;
print "\n";
print  $cfg->val('MONGODB', 'MONGODB_HOST');

print "\n";