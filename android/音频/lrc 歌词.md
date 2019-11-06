# 歌词解析

```kotlin
    fun analysisLrcFromFile(lrcFile: File): LrcBean? {
        try {
            if (!lrcFile.exists()) {
                return null
            }
            val fi = FileInputStream(lrcFile)
            val ir = InputStreamReader(fi)
            val bf = BufferedReader(ir)
            val lrcBean = readBufferReader(bf)
            bf.close()
            fi.close()
            ir.close()
            return lrcBean
        } catch (e: Exception) {
            YrLogger.d("LrcAnalysisUtils", e.toString())
            println(e.message)
        }
        return null
    }


    private fun analysisLrcStr(lrdStr: String): LrcBean? {
        try {
            val stringReader = StringReader(lrdStr)
            val bf = BufferedReader(stringReader)
            val lrcBean = readBufferReader(bf)
            bf.close()
            stringReader.close()
            return lrcBean
        } catch (e: Exception) {
            YrLogger.d("LrcAnalysisUtils", e.toString())
            println(e.message)

        }
        return null
    }

    private fun readBufferReader(bf: BufferedReader): LrcBean? {
        val lrcRowList = arrayListOf<LrcRow>()
        val lrcBean = LrcBean()
        try {
            for (line in bf.readLines()) {
                val lrcRows = analysisLrcLine(line)
                if (lrcRows.isNotEmpty()) {
                    lrcRowList.addAll(lrcRows)
                } else {
                    //否则可能是标题之类的
                    val title =
                        (Regex("\\[ti:.*?\\]").find(line)?.value)?.replace(Regex("\\[ti:|\\]"), "")
                    if (title != null) {
                        lrcBean.title = title
                        continue
                    }
                    val author =
                        (Regex("\\[ar:.*?\\]").find(line)?.value)?.replace(Regex("\\[ar:|\\]"), "")
                    if (author != null) {
                        lrcBean.author = author
                        continue
                    }
                    val album =
                        (Regex("\\[al:.*?\\]").find(line)?.value)?.replace(Regex("\\[al:|\\]"), "")
                    if (album != null) {
                        lrcBean.album = album
                        continue
                    }
                }
            }
            lrcRowList.add(
                LrcRow(
                    "00:00.00",
                    -3,
                    lrcBean.title,
                    "00:00"
                )
            )
            lrcRowList.add(
                LrcRow(
                    "00:00.00",
                    -2,
                    lrcBean.author,
                    "00:00"
                )
            )
            lrcRowList.add(
                LrcRow(
                    "00:00.00",
                    -1,
                    lrcBean.album,
                    "00:00"
                )
            )
            if (lrcRowList.size > 0) {
                lrcRowList.sort()
            }

            for (item in lrcRowList) {
                YrLogger.d("LrcAnalysisUtils", item.toString())
            }

            lrcBean.lrcRow = lrcRowList
            return lrcBean
        } catch (e: Exception) {
            println(e.message)
            YrLogger.d("LrcAnalysisUtils", e.toString())
        }
        return null
    }

    private fun analysisLrcLine(line: String?): List<LrcRow> {
        val lrcRowList = arrayListOf<LrcRow>()
        if (line == null || line.isEmpty()) {
            return emptyList()
        }
        val patten = "(\\[).{8}(\\])"
        val content = line.replace(Regex(patten), "")
        Regex(patten).findAll(line).toList().forEach {
            val timeStr = it.value.replace(Regex("\\[|\\]"), "")
            val lrcRow = LrcRow(
                timeStr,
                TimeUtils.string2TimeLong(timeStr),
                content,
                timeStr.replace(Regex("\\..*"), "")
            )
            lrcRowList.add(lrcRow)
        }
        return lrcRowList
    }
```