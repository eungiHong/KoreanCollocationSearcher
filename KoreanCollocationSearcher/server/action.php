<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<title>한국어 연어 검색기</title>

<link href="../assets/default.css" rel="stylesheet" type="text/css" media="all" />
<link href="../assets/fonts.css" rel="stylesheet" type="text/css" media="all" />
</head>

<body>
	<body>
	  <div id="wrapper">
	    <div id="menu-wrapper">
	      <div id="menu" class="container">
	        <div id="menu1">
	          <a href="../index.html">한국어 연어 검색기</a>
	        </div>
	        <div id="menu2">
	          <ul>
	            <li class="current_page_item"><a href="../index.html">Home</a></li>
	            <li><a href="#">About</a></li>
	            <!--<li><a href="#">Blog</a></li>-->
	            <!--<li><a href="#">Portfolio</a></li>-->
	            <li><a href="#">Contact</a></li>
	          </ul>
	        </div>
	      </div>
	      <!-- end #menu -->
	    </div>
			<div id="page" class="container2">
	      <div id="content2">

					<?php
					$query = $_POST["user_query"];
					$data = array();

					$dir_path = "../data";
					$dir_handle = opendir($dir_path."/");
					$flag = 0;
					while (false !== ($entry = readdir($dir_handle))) {
						if ($query === str_replace(".txt", "", $entry) and $query !== "." and $query !== "..") {
							$flag = 1;
							break;
						}
					}
					closedir($dir_handle);

					$target_path = $dir_path."/".$query.".txt";
					if ($flag == 1) {
						$file = fopen($target_path, "r");
						$count = 0;
						while (!feof($file)) {
							$count += 1;
							$line = fgets($file);
							$col_and_freq = explode("\t", $line);
							$data[] = $col_and_freq;
							# array_push($data, $col_and_freq);
							if ($count == 100) {
								break;
							}
						}
						fclose($file);
					} else {
						echo "검색 결과가 없습니다.<br><br>";
					}

					?>
					<table id="custom_table">
						<tr>
							<th>번호</th>
							<th>연어</th>
							<th>빈도수</th>
						</tr>
						<tr>
							<?php $count = 0;
							foreach($data as $row) :
							$count += 1 ?>
							<td><?php echo $count; ?></td>
							<td><?php echo $row[0]; ?></td>
							<td><?php echo $row[1]; ?></td>
						</tr>
						<?php endforeach; ?>
					</table>
				</div>
			</div>
		</div>
		<div id="copyright" class="container">
	    <p>&copy; Fernando. All rights reserved. | Design by <a href="http://templated.co" rel="nofollow">TEMPLATED</a>.</p>
	  </div>
</body>
</html>
