---
title: SOP_控件_AlertDialog.md
tags: android
grammar_cjkRuby: true
---

```java
            AlertDialog.Builder builder = new AlertDialog.Builder(context);
            builder.setTitle("Warning");
            builder.setMessage("You are forced to be offline. Please try to login again.");
            builder.setCancelable(false); // 设置为不可取消
            builder.setPositiveButton("OK", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    ActivityCollector.finishAll(); // 销毁所有的活动
                    Intent intent = new Intent(context , LoginActivity.class);
                    context.startActivity(intent); // 重新启动 LoginActivity
                }
            });
            builder.show();
```