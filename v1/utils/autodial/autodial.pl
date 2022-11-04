#!/usr/bin/perl

use strict;
use MongoDB;
use POSIX qw( strftime );
use Time::HiRes qw( sleep );
use Digest::SHA qw( sha1_hex );
use Data::Dumper qw(Dumper);
use integer;
use File::Basename;
use Cwd 'abs_path';
use Config::IniFiles;


my $file =  abs_path(__FILE__);
my $file_path = dirname($file);
my $base_path = dirname(dirname(dirname($file_path)));
my $local_config_file = abs_path("${base_path}/local_config.ini");
my $cfg = Config::IniFiles->new( -file => $local_config_file );

my $date = strftime "%F", localtime;
my $rit = strftime "%H-%M-%S", localtime;

my ( $collection, $call_counter, $max_sim_calls, $time_limit, $campaign, $aiserver ) = @ARGV;
my $dbs = $cfg->val('MONGODB', 'MONGODB_DB');

my $codename = lc $campaign;
my $aiserver_name = $aiserver;

my $mongo_username = $cfg->val('MONGODB', 'MONGODB_USERNAME');
my $mongo_password = $cfg->val('MONGODB', 'MONGODB_PASSWORD');
my $mongo_host = $cfg->val('MONGODB', 'MONGODB_HOST');
my $mongo_port = $cfg->val('MONGODB', 'MONGODB_PORT');

my $client = MongoDB::MongoClient->new( host => "mongodb://${mongo_host}:${mongo_port}/admin", username => $mongo_username, password => $mongo_password);

my $dbc = $client->get_database( $dbs );
my $col = $dbc->get_collection( $collection );
my %query = (
  status => 1,
  call_counter => { '$lt' => $call_counter+0 },
  calling => 0
);
my %qry_active_docs = (
  status => 1,
  call_counter => { '$lt' => $call_counter+0 },
  calling => 1
);

my $channel = "IAX2/out-test/";
my $context = "context-test";
my $run = 1;
my $active_docs = 1;
my $docs_counter = 1;
my $aiserver_status = 0;

while ( $run > 0) {
  my $time_now = strftime "%H:%M", localtime;
  my $tmp =  $col->find( \%query )->limit( 1 );
  my @docs = $tmp->all;
  my %qry_calling_counter = ( status => 1, calling => 1 );

  if ( $time_now eq $time_limit ) {
    print "Exit, time limit\n";
    Report();
    exit 0;
  }
  else{
    print "time limit: ${time_limit}. continue...\n";
  }

  my %qry_ready_docs = ('$or' => [
    { status => 0 },
    { status => 1 , call_counter => { '$gte' => 3 }}
  ]);

  my $ready_docs = $col->count( \%qry_ready_docs );
  my $calling_counter = $col->count( \%qry_calling_counter );
  my $docs_counter = $col->count( \%query );
  
  if ( $docs_counter == 0 ) {
    Active_docs();
    my $chkavail = $col->count( \%query );

    print "docs_counter: ${docs_counter}\n";
    #print "collection: ${collection}\n";
    #print Dumper(\%query);
    #print "\n";

    if ( $chkavail == 0 ) {
      print "chkavail: ${chkavail} exiting...\n";
      $run = 0;
      Report();
      exit 0;
    }
    else{
      print "chkavail: ${chkavail} continue...\n";
    }
    sleep 90;
  }
  else{
    print "docs_counter: ${docs_counter}\n";
  }

  my $index = 0;

  my $check_aiserver_status = `systemctl status ${aiserver_name} | grep Active`;
  chomp $check_aiserver_status;

  if ( $check_aiserver_status =~ m/running/i ) {
    $aiserver_status = 1; 
  }
  else {
    print "AISERVER DOWN\n";
    $aiserver_status = 0;
  }
  #my $live_calls = `asterisk -rx 'core show calls' |grep 'active calls'`;
  #my ($val, $key) = split / /, $live_calls;
  
  my $val = `asterisk -rx 'core show channels' |grep 'context-test'|wc -l`;
  my $key = "active calls";
  chomp $val;
  chomp $key;

  $val = $val+0;
  
  if ( $val < $max_sim_calls && $aiserver_status == 1 ) {
    my $time = strftime "%H:%M:%S", localtime;
    
    my $num_ident = $docs[$index]->{NUM_IDENT};
    #my $code = "$docs[$index]->{NUM_IDENT}$docs[$index]->{COD_EMPRESA}";
    my $number = "$docs[$index]->{TEL_CONTACTO}";
    my $callstatus = $docs[$index]->{calling}+0;
    my $phone_call_counter = $docs[$index]->{call_counter};
    my $family = $number;

    my $cid = sha1_hex("${time}${number}");
    my $phone = $number;
    #$phone =~ s/^56/9/g;
    $family =~ s/^\d{2}//g;
    #$code =~ s/-//g;

    if ( $number ) {
      if ( $callstatus == 0 ) {
        ##system "asterisk -rx 'database put ${family} code ${code}' > /dev/null";
        system "asterisk -rx 'database put ${family} cid ${cid}' > /dev/null";
        system "asterisk -rx 'channel originate ${channel}/${phone} extension ${phone}\@${context}'";
        print "EXECUTING: channel originate ${channel}/${phone} extension ${phone}\@${context}\n";
        Disable_record( $number );
        Disable_record_by_id( $num_ident );
        Log( $time, $num_ident , $number, $val, $ready_docs, $docs_counter, $active_docs, $phone_call_counter, $aiserver_status, $cid );
      }
      else{
        print "callstatus ${callstatus} for number ${number} as phone ${phone}\n";
      }
    }
    else{
      print "undefined number ${number} for num_ident ${num_ident}\n";
      DisableBadDocument_by_id( $num_ident );
    }
    $index ++;
  }
  else{
    print "max_sim_calls: ${val} limit: ${max_sim_calls}. aiserver_status: ${aiserver_status}\n";
  }
  sleep 0.5;
  $active_docs = $col->count( \%qry_active_docs );
}

sub Disable_record {
  my ( $number ) = @_;

  my %qry = ( "TEL_CONTACTO" => $number+0 );
  my %upt = (
    '$inc' => { call_counter => 1 },
    '$set' => { calling => 1 }
  );
  $col->update_many( \%qry , \%upt );
}

sub Disable_record_by_id {
  my ( $id ) = @_;
  my %qry = ( NUM_IDENT => $id );
  my %upt = ( '$set' => { calling => 1 });
  $col->update_many( \%qry , \%upt );
}

sub DisableBadDocument_by_id {
  my ( $id ) = @_;
  my %qry = ( NUM_IDENT => $id );
  my %upt = ( '$set' => { status => 0 });
  $col->update_many( \%qry , \%upt );
}

sub Active_docs {
  my %qry = ( status => 1, calling => 1, call_counter => { '$lt' => 3 });
  my %upt = ( '$set' => { calling => 0 });
  $col->update_many( \%qry , \%upt );
}

sub Log {
  my ( $time , $num_ident , $number, $active_calls, $ready_docs, $docs_counter, $remain , $call_counter , $aiserver_status, $cid ) = @_;
  my $out = "${date} ${time};";

  $out .= "${num_ident};";
  $out .= "${number};";
  $out .= "${active_calls};";
  $out .= "${ready_docs};";
  $out .= "${docs_counter};";
  $out .= "${remain};";
  $out .= "${call_counter};";
  $out .= "${aiserver_status};";
  $out .= "${cid}\n";

  my $filename = "/var/log/autodial_${codename}_${date}.log";
  open ( my $fh , '>>:encoding(UTF-8)', $filename ) or die "open $filename fail";
  print $fh $out;
  close $fh;
}

sub Report {
  print "Executing reportes\n";
  my $cmd = "python3 reporte_diario.py";

  system "$cmd";
}