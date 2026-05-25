$path = "C:\workspace\tsh\boilerplate\be\befw-app-server\pom.xml"
$content = Get-Content $path -Raw
$dependencies = @"

        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
        </dependency>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-database-postgresql</artifactId>
        </dependency>
"@

# Insert before the first </dependencies>
if ($content -match "</dependencies>") {
    $content = $content -replace "</dependencies>", "$dependencies`n    </dependencies>"
}

Set-Content $path $content -Encoding UTF8
