"Recursively looks through a folder structure and pulls out each .jpg and renames in to the grandparent and parent folder names then chucks them in the destination foolder."
	$sourcePath  = 'C:\Source'
	$destination = 'C:\Destination'

	# if the destination folder does not already exist, create it
		$null = New-Item -Path $destination -ItemType Directory
	if (!(Test-Path -Path $destination -PathType Container)) {
	}
	Get-ChildItem -Path $sourcePath -Filter '*.jpg' -File -Recurse | ForEach-Object {
		$newName = '{0} - {1} - {2}' -f $_.Directory.Parent.Name, $_.Directory.Name, $_.Name
		$_ | Copy-Item -Destination (Join-Path -Path $destination -ChildPath $newName)
	}