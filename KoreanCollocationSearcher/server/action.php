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
					$collocation_data = array();
					$example_data = array();
					$max_display = 50;

					# 연어를 추출해 놓은 파일 중에 검색어가 있는지 확인
					$dir_path = "../data/collocations";
					$dir_handle = opendir($dir_path."/");
					$flag = 0;
					while (false !== ($entry = readdir($dir_handle))) {
						if ($query === str_replace(".txt", "", $entry) and $query !== "." and $query !== "..") {
							$flag = 1;
							break;
						}
					}
					closedir($dir_handle); ?>

					<?php
					$target_path = $dir_path."/".$query.".txt";
					if ($flag == 1) :

						# 파일을 읽어 연어 목록 50개 가져오기
						$file = fopen($target_path, "r");
						$count = 0;
						while (!feof($file)) {
							$count += 1;
							$line = fgets($file);
							$col_and_freq = explode("\t", $line);
							$collocation_data[] = $col_and_freq;
							# array_push($collocation_data, $col_and_freq);
							if ($count == $max_display) {
								break;
							}
						}
						fclose($file); ?>

						<?php
						# 각 연어당 예시 50개 가져오기
						$dir_path = "../data/examples/쓰다";
						for ($cnt = 0; $cnt < $max_display; $cnt++) {
							$file = fopen($dir_path."/".$cnt.".txt", "r");
							$count = 0;
							$example_list = array();
							while (!feof($file)) {
								$count += 1;
								$line = fgets($file);
								$example_list[] = $line;
								if ($count == $max_display) {
									break;
								}
							}
							fclose($file);
							$example_data[] = $example_list;
						} ?>

						<!-- 테이블 전시 -->
						<table id="custom_table">
							<tr>
								<th>번호</th>
								<th>연어</th>
								<th>빈도수</th>
							</tr>
							<tr>
								<?php $count = 0;
								foreach($collocation_data as $row) :
								$count += 1 ?>
								<!-- 첫 번째 열: 번호 -->
								<td><?php echo $count; ?></td>
								<!-- 두 번째 열: 연어 및 그 예시 -->
								<td>
									<details>
										<summary><?php echo $row[0]; ?></summary>
										<?php foreach($example_data[$count] as $example) : ?>
											<li><?php echo $example; ?></li>
										<?php endforeach; ?>
									</details>
								</td>
								<!-- 세 번째 열: 빈도수 -->
								<td><?php echo $row[1]; ?></td>
							</tr>
							<?php endforeach; ?>
						</table>

					<?php else : echo "검색 결과가 없습니다.<br><br>"; ?>
					<?php endif; ?>

				</div>
			</div>
		</div>
		<div id="copyright" class="container">
	    <p>&copy; ehong. All rights reserved. | Design by <a href="http://templated.co" rel="nofollow">TEMPLATED</a>.</p>
	  </div>
</body>
</html>
